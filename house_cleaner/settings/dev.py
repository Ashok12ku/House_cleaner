from .base import *
from pathlib import Path
import os

# Development settings
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Database: use sqlite in dev
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Convenience: show emails in console during dev
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
