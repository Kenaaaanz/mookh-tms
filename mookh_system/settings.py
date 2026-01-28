import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'li3w(460q8x2tt!@0u1%!ecdk#)3u&iqu1yjksl@3aarkjpk!v'

DEBUG = True

ALLOWED_HOSTS = ['.onrender.com',
                 'localhost',
                 '127.0.0.1']

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'events',
    'invoices',
    'teams',
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

ROOT_URLCONF = 'mookh_system.urls'

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

WSGI_APPLICATION = 'mookh_system.wsgi.application'

#DATABASES = {
    #'default': {
        #'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': BASE_DIR / 'db.sqlite3',
    #}
#}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "mookh_tms",
        "USER": "postgres",
        "PASSWORD": "Ken@4427",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

#DATABASE_URL = os.environ.get('DATABASE_URL')

#if DATABASE_URL:
    #Production - PostgreSQL on Render
    #DATABASES = {
        #'default': dj_database_url.config(
            #default=DATABASE_URL,
            #conn_max_age=600,
            #conn_health_checks=True,
            #ssl_require=True  # Important for Render
        #)
    #}

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Mookh Color Scheme
MOOKH_PRIMARY = '#1E3A8A'  # Navy Blue
MOOKH_SECONDARY = '#3B82F6'  # Bright Blue
MOOKH_ACCENT = '#10B981'  # Emerald Green

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# In production, ensure these settings
if not DEBUG:
    # Security settings
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Static files
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    
    # Cache static files
    WHITENOISE_MAX_AGE = 31536000  # 1 year
    WHITENOISE_USE_FINDERS = True
    WHITENOISE_MANIFEST_STRICT = False
    WHITENOISE_ALLOW_ALL_ORIGINS = True

JAZZMIN_SETTINGS = {
    
    # Custom templates
    "changeform_format": "horizontal_tabs",
    "related_modal_active": True,
    
    # Custom dashboard
    "custom_template": {
        "admin/index.html": "admin/index.html",
    },
    
}