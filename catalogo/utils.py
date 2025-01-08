# utils.py modificado
from django.core.files import File
from catalogo.models import Libro, Categoria, ClasificacionEdad
import os
import random
from decimal import Decimal

def cargar_libros():
    """
    Carga los libros desde libro_1 hasta libro_22 en la carpeta media/libros
    """
    ruta_base = os.path.join('media', 'libros')
    
    # Crear algunas categorías predeterminadas
    categorias = []
    for nombre in ["Ficción", "No Ficción", "Infantil", "Aventura"]:
        categoria, _ = Categoria.objects.get_or_create(nombre=nombre)
        categorias.append(categoria)
    
    # Crear clasificaciones predeterminadas
    clasificaciones = []
    for nombre in ["Infantil", "Adolescente", "Adulto"]:
        clasificacion, _ = ClasificacionEdad.objects.get_or_create(nombre=nombre)
        clasificaciones.append(clasificacion)

    # Cargar libros del 1 al 22
    for i in range(1, 23):
        carpeta = f'libro_{i}'
        ruta_carpeta = os.path.join(ruta_base, carpeta)
        
        if not os.path.exists(ruta_carpeta):
            print(f"Carpeta no encontrada: {ruta_carpeta}")
            continue

        portada_path = os.path.join(ruta_carpeta, 'portada.jpg')
        libro_path = os.path.join(ruta_carpeta, 'libro.pdf')

        # Verificar que existan los archivos
        if not os.path.exists(portada_path):
            print(f"Falta portada.jpg en {carpeta}")
            continue
        if not os.path.exists(libro_path):
            print(f"Falta libro.pdf en {carpeta}")
            continue

        # Crear título a partir del nombre de la carpeta
        titulo = f"Libro {i}"

        # Verificar si el libro ya existe
        if Libro.objects.filter(titulo=titulo).exists():
            print(f"El libro '{titulo}' ya existe. Saltando...")
            continue

        try:
            # Crear el libro con valores predeterminados
            libro = Libro(
                titulo=titulo,
                autor="Autor Ejemplo",
                precio=Decimal('9.99'),  # Precio predeterminado
                categoria=random.choice(categorias),  # Categoría aleatoria
                clasificacion_edad=random.choice(clasificaciones)  # Clasificación aleatoria
            )

            # Adjuntar archivos
            with open(portada_path, 'rb') as portada_file:
                libro.portada.save(f'portada_{i}.jpg', File(portada_file), save=False)
            
            with open(libro_path, 'rb') as pdf_file:
                libro.archivo_pdf.save(f'libro_{i}.pdf', File(pdf_file), save=False)

            libro.save()
            print(f"Libro '{titulo}' cargado exitosamente")

        except Exception as e:
            print(f"Error al cargar el libro {titulo}: {str(e)}")

    print("Proceso de carga completado")