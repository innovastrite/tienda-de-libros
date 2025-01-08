import os
import django
import shutil
from decimal import Decimal
from django.core.files import File
from django.utils.text import slugify

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tienda_de_libros.settings')
django.setup()

from catalogo.models import Libro, Categoria, ClasificacionEdad

def crear_datos_base():
    # Crear categoría por defecto
    categoria, _ = Categoria.objects.get_or_create(
        nombre="General"
    )
    
    # Crear clasificación por defecto
    clasificacion, _ = ClasificacionEdad.objects.get_or_create(
        nombre="Todo público"
    )
    
    return categoria, clasificacion

def import_libros():  # Aquí está la definición de la función
    # Obtener categoría y clasificación base
    categoria, clasificacion = crear_datos_base()
    
    # Ruta base donde están los libros
    base_path = r'C:\Users\Public\tienda de libros\media\libros'
    
    # Iterar sobre cada carpeta de libro
    for i in range(1, 23):  # del 1 al 22
        libro_path = os.path.join(base_path, f'libro_{i}')
        if not os.path.exists(libro_path):
            print(f"La carpeta {libro_path} no existe")
            continue
        
        pdf_path = os.path.join(libro_path, 'libro.pdf')
        portada_path = os.path.join(libro_path, 'portada.jpg')
        
        if not os.path.exists(pdf_path) or not os.path.exists(portada_path):
            print(f"Faltan archivos en la carpeta libro_{i}")
            continue
            
        # Crear el libro
        libro = Libro(
            titulo=f"Libro {i}",  # Título temporal
            autor="Autor por definir",  # Autor temporal
            descripcion=f"Descripción del libro {i}",  # Descripción temporal
            precio=Decimal('0.00'),  # Precio por defecto
            categoria=categoria,
            clasificacion_edad=clasificacion,
        )
        
        # Guardar el libro primero para poder asociar los archivos
        libro.save()
        
        # Abrir y asociar los archivos
        with open(portada_path, 'rb') as portada_file:
            libro.portada.save(
                f'portada_{i}.jpg',
                File(portada_file),
                save=False
            )
            
        with open(pdf_path, 'rb') as pdf_file:
            libro.archivo_pdf.save(
                f'libro_{i}.pdf',
                File(pdf_file),
                save=False
            )
        
        # Guardar el libro con los archivos
        libro.save()
        
        print(f"Libro {i} importado correctamente")

if __name__ == '__main__':
    print("Iniciando importación de libros...")
    import_libros()  # Llamada a la función
    print("Importación completada")
