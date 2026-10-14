"""Base settings for house_cleaner project.
Common settings used by both dev and prod.
"""
# Paths
from pathlib import Path
import os
import importlib

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Lightweight .env loader and helpers (avoids dependency on external `environ` package)
def _read_dotenv(path):
    if not os.path.exists(path):
        return
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' not in line:
                    continue
                key, val = line.split('=', 1)
                key = key.strip()
                val = val.strip().strip('\"').strip("\'")
                # Don't overwrite existing environment
                if key not in os.environ:
                    os.environ[key] = val
    except Exception:
        pass

# load .env at project root if present
_read_dotenv(os.path.join(BASE_DIR, '.env'))

def env(key, default=None):
    return os.environ.get(key, default)

def env_bool(key, default=False):
    val = os.environ.get(key)
    if val is None:
        return default
    return str(val).lower() in ('1', 'true', 'yes', 'on')

def env_list(key, default=None):
    val = os.environ.get(key)
    if val is None:
        return default or []
    return [p.strip() for p in val.split(',') if p.strip()]

# SECURITY
SECRET_KEY = env('SECRET_KEY') or 'django-insecure-replace-for-dev'

# Email defaults (override via env)
EMAIL_BACKEND = env('EMAIL_BACKEND') or 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST') or 'smtp.gmail.com'
# allow numeric port from env
try:
    EMAIL_PORT = int(env('EMAIL_PORT') or 587)
except ValueError:
    EMAIL_PORT = 587
EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS', True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER') or ''
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD') or ''
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Media
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Payment keys
# Cashfree keys
CASHFREE_APP_ID = env('CASHFREE_APP_ID') or ''
CASHFREE_SECRET_KEY = env('CASHFREE_SECRET_KEY') or ''

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts.apps.AccountsConfig',
    'services',
    'bookings',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'house_cleaner.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'house_cleaner.wsgi.application'

# Database - overridden in dev/prod

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# keep existing auth model
AUTH_USER_MODEL = 'accounts.CustomUser'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Use WhiteNoise storage by default (if package available)
STATICFILES_STORAGE = os.environ.get('STATICFILES_STORAGE', 'whitenoise.storage.CompressedManifestStaticFilesStorage')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
