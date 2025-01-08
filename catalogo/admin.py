from django.contrib import admin
from .models import Libro, Categoria, ClasificacionEdad, Anuncio, Venta


# Admin para Categoria
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    search_fields = ['nombre']


# Admin para ClasificacionEdad
@admin.register(ClasificacionEdad)
class ClasificacionEdadAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    search_fields = ['nombre']


# Admin para Libro
@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 'autor', 'precio', 'categoria', 
        'clasificacion_edad', 'tiene_publicidad', 'activo'
    ]
    list_filter = ['categoria', 'clasificacion_edad', 'tiene_publicidad', 'activo']
    search_fields = ['titulo', 'autor']


# Admin para Anuncio
@admin.register(Anuncio)
class AnuncioAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'libro', 'fecha_inicio', 'fecha_fin', 'activo']
    list_filter = ['activo', 'fecha_inicio', 'fecha_fin']
    search_fields = ['titulo', 'libro__titulo']


# Admin para Venta
@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['libro', 'usuario', 'fecha_solicitud', 'cantidad', 'total', 'estado']
    list_filter = ['fecha_solicitud', 'estado']
    search_fields = ['libro__titulo', 'usuario__username']