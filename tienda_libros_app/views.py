from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import RegistroUsuarioForm, PerfilAutorForm
from .models import PerfilUsuario, Libro, Venta

def registro_usuario(request):
    """
    Vista para registrar un nuevo usuario.
    """
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, '¡Cuenta creada exitosamente!')
            return redirect('login')  # Cambiar a la URL del inicio de sesión si es diferente.
    else:
        form = RegistroUsuarioForm()
    return render(request, 'usuarios/registro.html', {'form': form})  # Ruta ajustada.

@user_passes_test(lambda u: u.is_staff)
def crear_autor(request):
    """
    Vista para que un administrador convierta un usuario en autor.
    """
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario')
        try:
            perfil = PerfilUsuario.objects.get(usuario_id=usuario_id)
            perfil.tipo_usuario = 'AUTOR'
            perfil.save()
            messages.success(request, '¡Usuario convertido a autor exitosamente!')
        except PerfilUsuario.DoesNotExist:
            messages.error(request, 'Usuario no encontrado.')
    
    # Filtrar usuarios que son clientes.
    usuarios = User.objects.filter(perfilusuario__tipo_usuario='CLIENTE')
    return render(request, 'usuarios/crear_autor.html', {'usuarios': usuarios})  # Ruta ajustada.

@login_required
def panel_autor(request):
    """
    Vista para mostrar el panel de autor con libros y ventas asociadas.
    """
    if not request.user.perfilusuario.tipo_usuario == 'AUTOR':
        messages.error(request, 'No tienes permisos de autor.')
        return redirect('home')  # Cambiar a la URL de inicio si es diferente.
    
    # Obtener libros y ventas relacionadas con el autor actual.
    libros = Libro.objects.filter(autor_usuario=request.user)
    ventas = Venta.objects.filter(libro__autor_usuario=request.user)
    
    context = {
        'libros': libros,
        'total_ventas': sum(v.total for v in ventas if v.estado == 'CONFIRMADO'),
        'libros_vendidos': ventas.filter(estado='CONFIRMADO').count()
    }
    return render(request, 'usuarios/panel_autor.html', context)  # Ruta ajustada.
