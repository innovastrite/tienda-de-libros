from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.core.validators import MinValueValidator
import uuid
from django.conf import settings  # Para usar AUTH_USER_MODEL


# Modelo para el perfil de usuario
class PerfilUsuario(models.Model):
    TIPOS_USUARIO = [
        ('CLIENTE', 'Cliente'),
        ('AUTOR', 'Autor'),
    ]
    
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tipo_usuario = models.CharField(max_length=10, choices=TIPOS_USUARIO, default='CLIENTE')
    biografia = models.TextField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.tipo_usuario}"

    class Meta:
        verbose_name_plural = "Perfiles de usuario"

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['nombre']
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre

class ClasificacionEdad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['nombre']
        verbose_name_plural = "Clasificaciones de edad"

    def __str__(self):
        return self.nombre

class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)  # Hacemos descripcion opcional
    precio = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.CASCADE, 
        related_name="libros"
    )
    clasificacion_edad = models.ForeignKey(
        ClasificacionEdad, 
        on_delete=models.CASCADE, 
        related_name="libros"
    )
    portada = models.ImageField(
        upload_to='portadas/',
        null=True,
        blank=True
    )
    archivo_pdf = models.FileField(
        upload_to='libros_pdf/',
        null=True,
        blank=True
    )
    tiene_publicidad = models.BooleanField(default=False)
    publicidad_inicio = models.DateField(null=True, blank=True)
    publicidad_fin = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_venta = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name_plural = "Libros"

    @property
    def es_gratis(self):
        return self.precio == 0

    def __str__(self):
        return self.titulo

class Anuncio(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(
        upload_to='anuncios/',
        null=True,
        blank=True
    )
    libro = models.ForeignKey(
        Libro,
        on_delete=models.CASCADE,
        related_name="anuncios",
        null=True,
        blank=True
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['-fecha_inicio']
        verbose_name_plural = "Anuncios"

    def __str__(self):
        return self.titulo

class Venta(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADO', 'Confirmado'),
    ]
    
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)
    token_descarga = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ['-fecha_solicitud']
        verbose_name_plural = "Ventas"

    def __str__(self):
        return f"Venta de {self.libro.titulo} - {self.usuario.username}"

    def generar_token(self):
        if not self.token_descarga:
            self.token_descarga = str(uuid.uuid4())
            self.save()

class DescargaLibro(models.Model):
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='descargas')
    usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)
    fecha_descarga = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=[('PENDIENTE', 'Pendiente de confirmación'),
                 ('CONFIRMADO', 'Confirmado para descarga'),
                 ('DESCARGADO', 'Descargado'),
                 ('EXPIRADO', 'Expirado')],
        default='PENDIENTE'
    )
    token_descarga = models.CharField(max_length=100, unique=True, null=True, blank=True)

    class Meta:
        ordering = ['-fecha_solicitud']
        verbose_name_plural = "Descargas de libros"

    def __str__(self):
        return f"Descarga de {self.libro.titulo} por {self.usuario.username}"

    def generar_token(self):
        self.token_descarga = str(uuid.uuid4())
        self.save()

# Agregada la clase NotificacionAdmin
class NotificacionAdmin(models.Model):
    descarga = models.ForeignKey(DescargaLibro, on_delete=models.CASCADE, related_name='notificaciones')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name_plural = "Notificaciones admin"

    def __str__(self):
        return f"Notificación de descarga - {self.descarga}"
