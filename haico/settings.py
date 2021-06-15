"""
Django settings for haico project.

Generated by 'django-admin startproject' using Django 3.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
import secrets
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
from django.urls import reverse_lazy

BASE_DIR = Path(__file__).resolve().parent.parent

# Fix bootstrap-breadcrumbs not working with Django 4
import django
from django.utils.encoding import smart_str
django.utils.encoding.smart_text = smart_str

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Host specific

# Configure this
HOST_DOMAIN = 'info.hadiko.de'
BASE_URL = f'https://{HOST_DOMAIN}'
ALLOWED_HOSTS = [HOST_DOMAIN, '127.0.0.1']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'infoscreen.apps.InfoscreenConfig',
    'django_bootstrap_breadcrumbs',
    'crispy_forms',
    'crispy_bootstrap4',
    'django_tables2',
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'haico.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'APP_DIRS': True,
        'OPTIONS': {
            'autoescape': False,  # Jinja2 used for plain text only
            'trim_blocks': True,
            'lstrip_blocks': True,
        }
    }
]

WSGI_APPLICATION = 'haico.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DB_DIR = 'databases'
os.makedirs(DB_DIR, exist_ok=True)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, DB_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True

gettext = lambda s: s
LANGUAGES = (
    ('en', gettext('English')),
    ('de', gettext('German')),
)

LOCALE_PATHS = (
    Path(BASE_DIR, 'locale'),
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

if not DEBUG:
    STATIC_ROOT = os.path.join(BASE_DIR, "static/")
else:
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'static'),
    ]

# Infoscreen files

INFOSCREEN_FILES_FOLDER = 'infoscreen-content'
MEDIA_URL = f'/{INFOSCREEN_FILES_FOLDER}/'
MEDIA_ROOT = INFOSCREEN_FILES_FOLDER

INFOSCREEN_TARGET_WIDTH = 1920
INFOSCREEN_TARGET_HEIGHT = 1080

# Templates

BREADCRUMBS_TEMPLATE = 'django_bootstrap_breadcrumbs/bootstrap4.html'
CRISPY_TEMPLATE_PACK = 'bootstrap4'
DJANGO_TABLES2_TEMPLATE = "django_tables2/bootstrap4.html"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging

LOG_DIR = 'log/'
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('log', 'debug.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# E-Mail

STAFF_EMAIL_ADDRESSES = ['infoscreen@hadiko.de']  # <- Configure this

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = 'log/mails'
else:
    # Configure the following stuff
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_USE_TLS = True
    EMAIL_HOST = 'mail.hadiko.de'
    EMAIL_PORT = 587
    DEFAULT_FROM_EMAIL = 'infoscreen@hadiko.de'

# Auth

AUTHLIB_OAUTH_CLIENTS = {
    'org': {
        'client_id': os.getenv('OAUTH_CLIENT_ID'),
        'client_secret': os.getenv('OAUTH_CLIENT_SECRET'),
    }
}

LOGIN_URL = reverse_lazy('login')

# Configure this
ADMIN_GROUP = 'ak-infoscreen'
OAUTH_USERNAME_CLAIM = 'hadiko_username'
OAUTH_GROUP_CLAIM = 'hadiko_groups'
OAUTH_EMAIL_CLAIM = 'hadiko_email'
OPENID_CONF_URL = 'https://sso.hadiko.de/auth/realms/hadiko/.well-known/openid-configuration'
OAUTH_CLIENT_SCOPES = 'openid hadiko-email hadiko-username hadiko-groups'
