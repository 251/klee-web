"""
Django settings for web project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
from time import gmtime, strftime

import string
import random

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Add path of klee-web python code to allow importing of worker code
sys.path.insert(0, os.path.join(BASE_DIR, ".."))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if os.environ['DEVELOPMENT'] == "1" else False

# If we're in debug mode, generate a random key
# so that we don't need to provide one

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")

if DEBUG:
    # Long but silences flake8
    k = [random.SystemRandom().choice(string.ascii_letters + string.digits)
         for _ in range(50)]
    SECRET_KEY = ''.join(k)

ALLOWED_HOSTS = ['*']

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Paths for Django to find templates
        'DIRS': [
            os.path.join(BASE_DIR, 'frontend/templates'),
            os.path.join(BASE_DIR, 'control_panel/templates')
        ],
        # Controls whether Django checks for templates inside apps
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "frontend.context_processors.global_vars",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect"
            ],
        }
    }
]

# Application definition
INSTALLED_APPS = (
    'frontend',
    'control_panel',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_nested',
    'rest_framework_social_oauth2',
    'oauth2_provider',
    'social_django',
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'urls'

WSGI_APPLICATION = 'wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get("DB_NAME", ""),
        'USER': os.environ.get("DB_USER", ""),
        'PASSWORD': os.environ.get("DB_PASSWORD", ""),
        'HOST': os.environ.get("DB_HOST", ""),
        'PORT': os.environ.get("DB_PORT", ""),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = strftime("%Z", gmtime())

USE_I18N = True

USE_L10N = True

AUTHENTICATION_BACKENDS = (
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.github.GithubOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(os.path.dirname(__file__), 'frontend', 'static')
AUTH_USER_MODEL = 'frontend.User'

# Keys and secrets used to authenticate with Google, GitHub and Facebook
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('GOOGLE_OAUTH_KEY') or ''
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('GOOGLE_OAUTH_SECRET') or ''
SOCIAL_AUTH_GITHUB_KEY = os.environ.get('GITHUB_OAUTH_KEY') or ''
SOCIAL_AUTH_GITHUB_SECRET = os.environ.get('GITHUB_OAUTH_SECRET') or ''
SOCIAL_AUTH_FACEBOOK_KEY = os.environ.get('FB_OAUTH_KEY') or ''
SOCIAL_AUTH_FACEBOOK_SECRET = os.environ.get('FB_OAUTH_SECRET') or ''
# Facebook login automatically redirects to /accounts/profile,
# which does not exist, so we enforce redirection to /
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
    ),
}
