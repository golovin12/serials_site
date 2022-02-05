import os
from pathlib import Path
from keys_settings import keys_settings


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = keys_settings.SECRET_KEY

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "mysite.com", "192.168.43.178"]

INSTALLED_APPS = [
    'authorization.apps.AuthorizationConfig',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',

    'taggit',

    'controls.apps.ControlsConfig',
    'serials.apps.SerialsConfig',
    'subscribes.apps.SubscribesConfig',
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
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
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'serials',
        'USER': 'postgres',
        'PASSWORD': keys_settings.DB_PASSWORD,
    }
}

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

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'authorization.authentication.EmailAuthBackend',
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

TAGGIT_CASE_INSENSITIVE = True

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

LOGIN_REDIRECT_URL = '/serials/categories/'
LOGIN_URL = '/authorization/login/'
LOGOUT_URL = '/authorization/logout/'

DEFAULT_CHARSET = 'utf-8'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]