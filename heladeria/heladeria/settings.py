from pathlib import Path
import os
import environ

# === BASE DEL PROYECTO ===
BASE_DIR = Path(__file__).resolve().parent.parent

# === VARIABLES DE ENTORNO ===
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# === CONFIGURACIÓN GENERAL ===
SECRET_KEY = env('SECRET_KEY', default='django-insecure-key-fallback')
DEBUG = env.bool('DEBUG', default=True)


# === APLICACIONES INSTALADAS ===
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Apps locales
    'core',
    'clientes',
    'productos',
    'ventas',
    'marketing',

    # Librerías externas
    'widget_tweaks',
]

# === MIDDLEWARE ===
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# === URLS Y WSGI ===
ROOT_URLCONF = 'heladeria.urls'
WSGI_APPLICATION = 'heladeria.wsgi.application'

# === TEMPLATES ===
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'core' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.roles',
            ],
        },
    },
]

# === BASE DE DATOS ===
# Para pruebas rápidas


# Permitir la IP pública de tu servidor
ALLOWED_HOSTS = ['TU_IP_PUBLICA']

# Configurar la base de datos RDS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # o 'django.db.backends.mysql'
        'NAME': 'db-heladeria',                     # nombre de la base de datos
        'USER': 'admin',                            # usuario
        'PASSWORD': 'Lolita123-',                   # contraseña
        'HOST': 'db-heladeria.cjiqg66ya4w3.us-east-1.rds.amazonaws.com',  # endpoint RDS
        'PORT': '3306',                             # puerto (PostgreSQL)
    }
}

# Para pruebas rápidas, no hace falta configurar STATIC_ROOT


# === VALIDADORES DE CONTRASEÑA ===
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# === INTERNACIONALIZACIÓN ===
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# === ARCHIVOS ESTÁTICOS Y MEDIA ===
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "core" / "static"]
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# === LOGIN / LOGOUT ===
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/clientes/login/'
LOGOUT_REDIRECT_URL = '/clientes/login/'

# === SESIONES ===
SESSION_COOKIE_AGE = 60 * 60 * 2  # 2 horas
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = 'Lax'

# === CONFIGURACIÓN DE EMAIL ===
if DEBUG:
    # Modo desarrollo (Mac)
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    DEFAULT_FROM_EMAIL = "noreply@miapp.local"
else:
    # Producción (AWS con Gmail)
    EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
    EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
    EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
    DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

# === CONFIGURACIÓN DE ARCHIVOS GRANDES ===
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5 MB
FILE_UPLOAD_PERMISSIONS = 0o644

# === AUTO FIELD ===
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATIC_ROOT = BASE_DIR / "staticfiles"

