from pathlib import Path
import os
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY', default='django-insecure-key-fallback')
DEBUG = env.bool('DEBUG', default=True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['127.0.0.1', 'localhost'])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Apps propias
    'core',
    'clientes',
    'productos',
    'ventas',
    'marketing',

    # Librerías externas
    'widget_tweaks',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'heladeria.urls'

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
                'core.context_processors.roles',  # o roles_usuario según tu código
            ],
        },
    },
]

WSGI_APPLICATION = 'heladeria.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DB_NAME', default='heladeria_db'),
        'USER': env('DB_USER', default='root'),
        'PASSWORD': env('DB_PASSWORD', default='root'),
        'HOST': env('DB_HOST', default='127.0.0.1'),
        'PORT': env('DB_PORT', default='8889'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "core" / "static"]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/clientes/login/'
LOGOUT_REDIRECT_URL = '/clientes/login/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuraciones de sesión
# Duración de la cookie de sesión (en segundos)
SESSION_COOKIE_AGE = 60 * 60 * 2  # 2 horas

# ¿La sesión expira al cerrar el navegador?
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Cada vez que se hace una petición, se actualiza la expiración
SESSION_SAVE_EVERY_REQUEST = True

# Seguridad de las cookies
SESSION_COOKIE_SECURE = False  # Solo en producción con HTTPS

# Restricción SameSite (protección CSRF)
SESSION_COOKIE_SAMESITE = 'Lax'  # Puede ser 'Lax', 'Strict' o 'None' (+ Secure)
