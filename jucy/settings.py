"""
Django settings for jucy project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = None  # FILL ME

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap_form_horizontal',
    'social.apps.django_app.default',
    #'rest_framework',
    'web',
    'widget',
    'api',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    # Do not enable any database-backed
    'django.contrib.auth.backends.ModelBackend',
    'social.backends.github.GithubOAuth2',
)

ROOT_URLCONF = 'jucy.urls'

WSGI_APPLICATION = 'jucy.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'web/static'),
    os.path.join(BASE_DIR, 'widget/static'),
)
STATIC_URL = '/_static/'

# Social auth settings

LOGIN_URL = '/_oauth/login/github'
LOGIN_REDIRECT_URL = '/_pick'
LOGIN_ERROR_URL = '/_loginerror'

SOCIAL_AUTH_GITHUB_SCOPE = [
    'user',
    'read:org',
    'repo',
]

DEFAULT_AVATAR = 'http://localhost:8000/_static/img/defaultavatar.png'

# Dev app id/secret
SOCIAL_AUTH_GITHUB_KEY = None  # FILL ME
SOCIAL_AUTH_GITHUB_SECRET = None  # FILL ME

# Jucybot
JUCY_BOT_LOGIN = 'JucyBot'
JUCY_BOT_OAUTH_TOKEN = None  # FILL ME

# Webhooks callback URL
WEBHOOKS_CALLBACK_URL = (
    'https://jucy.io/%(owner)s/%(repository)s/_webhooks/%(hooktype)s')
WEBHOOKS_SECRET_KEY = None  # FILL ME

LANDING_MODE = False

AWS_SES_RETURN_PATH = 'jucybot@jucy.io'

try:
    from local_settings import *
except ImportError:
    pass
