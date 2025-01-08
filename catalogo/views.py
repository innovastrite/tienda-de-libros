from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Case, When, Value, BooleanField, Q, Sum
from django.http import HttpResponse, Http404, FileResponse
from django.utils import timezone
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from .models import (
    Libro, Categoria, ClasificacionEdad, Anuncio, 
    Venta, DescargaLibro, NotificacionAdmin, PerfilUsuario
)
import os
import uuid

def es_admin(user):
    """Verifica si un usuario es administrador"""
    return user.is_staff and user.is_active

def es_autor(user):
    """Verifica si un usuario es autor"""
    try:
        return user.is_active and user.perfilusuario.tipo_usuario == 'AUTOR'
    except PerfilUsuario.DoesNotExist:
        return False

@user_passes_test(es_admin)
def crear_autor(request):
    """Vista para que un administrador convierta usuarios a autores"""
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario')
        try:
            usuario = User.objects.get(id=usuario_id, perfilusuario__tipo_usuario='CLIENTE')
            perfil = usuario.perfilusuario
            perfil.tipo_usuario = 'AUTOR'
            perfil.save(update_fields=['tipo_usuario'])
            messages.success(request, f'El usuario {usuario.username} ahora es autor.')
            return redirect('admin_notificaciones')
        except User.DoesNotExist:
            messages.error(request, 'Usuario no encontrado.')
    
    usuarios = User.objects.filter(perfilusuario__tipo_usuario='CLIENTE')
    return render(request, 'usuarios/crear_autor.html', {'usuarios': usuarios})

@login_required
@user_passes_test(es_autor)
def panel_autor(request):
    """Panel de control para autores"""
    libros = Libro.objects.filter(
        autor=request.user.get_full_name() or request.user.username
    )
    
    ventas = Venta.objects.filter(
        libro__in=libros,
        estado='CONFIRMADO'
    )
    
    estadisticas = {
        'total_ventas': ventas.aggregate(total=Sum('total'))['total'] or 0,
        'libros_vendidos': ventas.count(),
        'libros_publicados': libros.count()
    }

    return render(request, 'usuarios/panel_autor.html', {
        'libros': libros,
        'estadisticas': estadisticas
    })

def registro_usuario(request):
    """Vista para registro de nuevos usuarios"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                PerfilUsuario.objects.create(
                    usuario=user,
                    tipo_usuario='CLIENTE'
                )
            messages.success(request, '¡Cuenta creada exitosamente!')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'catalogo/registro.html', {'form': form})

def lista_libros(request):
    """Vista para listar libros con filtros"""
    today = timezone.now().date()
    
    libros = Libro.objects.filter(activo=True).select_related(
        'categoria', 'clasificacion_edad'
    ).annotate(
        publicidad_activa=Case(
            When(
                tiene_publicidad=True,
                publicidad_inicio__lte=today,
                publicidad_fin__gte=today,
                then=Value(True)
            ),
            default=Value(False),
            output_field=BooleanField(),
        )
    )
    
    filtros = {}
    if clasificacion := request.GET.get('clasificacion'):
        filtros['clasificacion_edad_id'] = clasificacion
    
    if precio_max := request.GET.get('precio'):
        try:
            filtros['precio__lte'] = float(precio_max)
        except ValueError:
            pass
    
    if request.GET.get('gratis'):
        filtros['precio'] = 0
    
    libros = libros.filter(**filtros).order_by('-publicidad_activa', 'titulo')
    
    paginator = Paginator(libros, 9)
    page = request.GET.get('page')
    libros_paginados = paginator.get_page(page)

    context = {
        'libros': libros_paginados,
        'categorias': Categoria.objects.all(),
        'clasificaciones': ClasificacionEdad.objects.all(),
        'anuncios': Anuncio.objects.filter(
            activo=True,
            fecha_inicio__lte=today,
            fecha_fin__gte=today
        ).select_related('libro'),
    }
    return render(request, 'catalogo/lista_libros.html', context)

def detalle_libro(request, id):
    """Vista para ver el detalle de un libro"""
    libro = get_object_or_404(
        Libro.objects.select_related('categoria', 'clasificacion_edad'),
        id=id,
        activo=True
    )
    
    context = {
        'libro': libro,
        'compra_confirmada': None
    }
    
    if request.user.is_authenticated:
        context['compra_confirmada'] = Venta.objects.filter(
            libro=libro,
            usuario=request.user,
            estado='CONFIRMADO'
        ).first()
    
    return render(request, 'catalogo/detalle_libro.html', context)

@login_required
def solicitar_descarga(request, libro_id):
    """Vista para solicitar la descarga de un libro"""
    libro = get_object_or_404(Libro, id=libro_id, activo=True)
    
    descarga_activa = DescargaLibro.objects.filter(
        libro=libro,
        usuario=request.user,
        estado__in=['PENDIENTE', 'CONFIRMADO']
    ).first()
    
    if descarga_activa:
        return render(request, 'catalogo/descarga_pendiente.html', {
            'descarga': descarga_activa
        })
    
    with transaction.atomic():
        descarga = DescargaLibro.objects.create(
            libro=libro,
            usuario=request.user,
            estado='PENDIENTE'
        )
        NotificacionAdmin.objects.create(descarga=descarga)
    
    return render(request, 'catalogo/descarga_solicitada.html', {
        'descarga': descarga
    })

@user_passes_test(es_admin)
def confirmar_descarga(request, descarga_id):
    """Vista para confirmar una solicitud de descarga"""
    descarga = get_object_or_404(DescargaLibro, id=descarga_id, estado='PENDIENTE')
    
    if request.method == 'POST':
        with transaction.atomic():
            descarga.estado = 'CONFIRMADO'
            descarga.fecha_confirmacion = timezone.now()
            descarga.token_descarga = str(uuid.uuid4())
            descarga.save(update_fields=['estado', 'fecha_confirmacion', 'token_descarga'])
            
            NotificacionAdmin.objects.filter(descarga=descarga).update(leida=True)
            messages.success(request, 'Descarga confirmada exitosamente.')
            
        return redirect('admin_notificaciones')
    
    return render(request, 'catalogo/confirmar_descarga.html', {'descarga': descarga})

@login_required
def descargar_libro(request, token):
    """Vista para descargar un libro"""
    descarga = get_object_or_404(
        DescargaLibro,
        token_descarga=token,
        usuario=request.user,
        estado='CONFIRMADO'
    )
    
    if not descarga.libro.pdf:
        raise Http404("El archivo no está disponible.")
    
    try:
        return FileResponse(
            descarga.libro.pdf.open('rb'),
            as_attachment=True,
            filename=f"{descarga.libro.titulo}.pdf"
        )
    except FileNotFoundError:
        raise Http404("El archivo no se encuentra en el servidor.")

@user_passes_test(es_admin)
def admin_notificaciones(request):
    """Vista para el panel de notificaciones del admin"""
    notificaciones = NotificacionAdmin.objects.select_related(
        'descarga__libro', 
        'descarga__usuario'
    ).filter(leida=False).order_by('-fecha_creacion')
    
    return render(request, 'catalogo/admin_notificaciones.html', {
        'notificaciones': notificaciones
    })

@login_required
def solicitar_compra(request, libro_id):
    """Vista para solicitar la compra de un libro"""
    libro = get_object_or_404(Libro, id=libro_id, activo=True)
    
    compra_existente = Venta.objects.filter(
        libro=libro,
        usuario=request.user,
        estado='CONFIRMADO'
    ).first()
    
    if compra_existente:
        messages.info(request, 'Ya has comprado este libro.')
        return redirect('estado_compra', venta_id=compra_existente.id)
    
    if request.method == 'POST':
        try:
            cantidad = int(request.POST.get('cantidad', 1))
            if cantidad < 1:
                raise ValueError("La cantidad debe ser mayor a 0")
            
            venta = Venta.objects.create(
                libro=libro,
                usuario=request.user,
                cantidad=cantidad,
                total=libro.precio * cantidad,
                estado='PENDIENTE'
            )
            return redirect('estado_compra', venta_id=venta.id)
            
        except ValueError as e:
            messages.error(request, str(e))
    
    return render(request, 'catalogo/solicitar_compra.html', {'libro': libro})

@login_required
def estado_compra(request, venta_id):
    """Vista para ver el estado de una compra"""
    venta = get_object_or_404(
        Venta.objects.select_related('libro'),
        id=venta_id,
        usuario=request.user
    )
    return render(request, 'catalogo/estado_compra.html', {'venta': venta})

@user_passes_test(es_admin)
def admin_ventas(request):
    """Vista para el panel de ventas del admin"""
    ventas = Venta.objects.select_related('libro', 'usuario').filter(
        estado='PENDIENTE'
    ).order_by('-fecha_solicitud')
    
    return render(request, 'catalogo/admin_ventas.html', {
        'ventas_pendientes': ventas
    })

@user_passes_test(es_admin)
def confirmar_venta(request, venta_id):
    """Vista para confirmar una venta por parte del admin"""
    venta = get_object_or_404(Venta, id=venta_id, estado='PENDIENTE')
    
    if request.method == 'POST':
        with transaction.atomic():
            venta.estado = 'CONFIRMADO'
            venta.fecha_confirmacion = timezone.now()
            venta.token_descarga = str(uuid.uuid4())
            venta.save(update_fields=['estado', 'fecha_confirmacion', 'token_descarga'])
            
            venta.libro.ultima_venta = timezone.now()
            venta.libro.save(update_fields=['ultima_venta'])
            
            messages.success(request, 'Venta confirmada exitosamente.')
        return redirect('admin_ventas')
    
    return render(request, 'catalogo/confirmar_venta.html', {'venta': venta})

@login_required  # Añadir este decorador para asegurar que hay un usuario autenticado
def registrar_venta(request, id):
    libro = get_object_or_404(Libro, id=id, activo=True)
    if request.method == 'POST':
        try:
            cantidad = int(request.POST.get('cantidad', 1))
            if cantidad <= 0:
                raise ValueError("La cantidad debe ser positiva")

            total = libro.precio * cantidad
            # Añadir el usuario a la creación de la venta
            Venta.objects.create(
                libro=libro,
                cantidad=cantidad,
                total=total,
                usuario=request.user,  # Añadir el usuario actual
                estado='PENDIENTE'  # Añadir el estado inicial
            )
            libro.ultima_venta = timezone.now()
            libro.save(update_fields=['ultima_venta'])
            messages.success(request, 'Venta registrada exitosamente.')
            return redirect('detalle_libro', id=id)
        except (ValueError, TypeError):
            messages.error(request, 'Error al registrar la venta.')
    return render(request, 'catalogo/registrar_venta.html', {'libro': libro})
def historial_ventas(request, libro_id):
    """Vista para ver el historial de ventas de un libro"""
    libro = get_object_or_404(Libro, id=libro_id)
    ventas = Venta.objects.filter(libro=libro).order_by('-fecha_solicitud')
    
    total_ventas = ventas.aggregate(total=Sum('total'))['total'] or 0
    
    context = {
        'libro': libro,
        'ventas': ventas,
        'totales': {
            'total_ventas': total_ventas,
            'total_autor': total_ventas * 0.9,  # 90% para el autor
            'total_tienda': total_ventas * 0.1,  # 10% para la tienda
        },
    }
    return render(request, 'catalogo/historial_ventas.html', context)

@user_passes_test(es_admin)
def borrar_historial(request, libro_id):
    """Vista para borrar el historial de ventas de un libro"""
    if request.method == 'POST':
        libro = get_object_or_404(Libro, id=libro_id)
        with transaction.atomic():
            Venta.objects.filter(libro=libro).delete()
            libro.ultima_venta = None
            libro.save(update_fields=['ultima_venta'])
            messages.success(request, 'Historial borrado exitosamente.')
    return redirect('detalle_libro', id=libro_id)