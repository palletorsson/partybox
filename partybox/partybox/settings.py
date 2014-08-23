"""
Django settings for partybox project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


PROJECT_ROOT        = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
STATIC_ROOT         = os.path.join(PROJECT_ROOT, 'static')
print STATIC_ROOT
STATIC_URL 			= STATIC_ROOT+"/" 
MEDIA_ROOT          = os.path.join(PROJECT_ROOT, 'media')
MEDIA_URL = "/media/"
#MEDIA_URL 			= MEDIA_ROOT+"/"
STATIC_URL_PLAIN = "/static/"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ddxyvd-hqr^bqs*ck87t8dq5!+jd3q@kj3acnm9kuvn+zmhan4'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'grappelli',
    'filebrowser',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.publication',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'partybox.urls'

WSGI_APPLICATION = 'partybox.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/


TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
<<<<<<< HEAD

    '/home/pi/partybox/partybox/partybox/theme/templates/',
=======
	'/home/palle/Project/django/partybox/partybox/partybox/theme/templates/',
>>>>>>> d871339010d6c7d4753fb40bbf9fa8dc5fc6f2fc
)

try:
    from .local_settings import *
except ImportError:
    pass
