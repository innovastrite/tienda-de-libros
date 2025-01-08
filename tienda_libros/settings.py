import os
from pathlib import Path

# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Modo de depuración
DEBUG = True

# Hosts permitidos
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Llave secreta (mantenla segura en producción)
SECRET_KEY = 'tiendaamiga32'

# Configuración de archivos estáticos
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Configuración de archivos multimedia
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# Configuración principal de la aplicación
ROOT_URLCONF = 'tienda_libros.urls'

# Aplicaciones instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',  # Añadido para soporte de mensajes
    'django.contrib.staticfiles',
    'catalogo',  # App principal
    'tienda_libros_app',  # App adicional, si existe
]

# Middleware configurado en el orden correcto
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # Debe ir antes de AuthenticationMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',  # Añadido para soporte de mensajes
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

import os
from pathlib import Path

# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuración de base de datos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # La base de datos será un archivo SQLite en el directorio base
    }
}

# Configuración de plantillas
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'catalogo/templates',  # Carpeta de plantillas de la app catalogo
            BASE_DIR / 'templates',  # Directorio adicional para plantillas generales
        ],
        'APP_DIRS': True,  # Permite cargar plantillas de las aplicaciones instaladas
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',  # Agregado para manejar archivos multimedia
            ],
        },
    },
]


# Configuración de idioma y zona horaria
LANGUAGE_CODE = 'es-es'  # Español
TIME_ZONE = 'UTC'  # Hora universal coordinada
USE_I18N = True  # Activación de internacionalización
USE_L10N = True  # Activación de localización
USE_TZ = True  # Activación de zona horaria

# Configuración adicional para archivos estáticos
STATIC_URL = '/static/'  # URL para acceder a los archivos estáticos
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # Ubicación de los archivos estáticos (como CSS, JS, imágenes)
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Carpeta donde se recopilan los archivos estáticos cuando se ejecuta 'collectstatic'

# Configuración de archivos multimedia (por ejemplo, PDFs, imágenes)
MEDIA_URL = '/media/'  # URL para acceder a los archivos multimedia
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Carpeta donde se guardan los archivos multimedia

# Configuración de autenticación
LOGIN_URL = 'login'  # Redirige a la página de login si no está autenticado
LOGIN_REDIRECT_URL = 'lista_libros'  # Redirige a la página de libros después de iniciar sesión

# Configuración de mensajes
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
