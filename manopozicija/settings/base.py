import collections
import json
import os
import pathlib

Size = collections.namedtuple('Size', ['width', 'height'])

if 'MANOPOZICIJA_DIR' in os.environ:
    PROJECT_DIR = pathlib.Path(os.environ['MANOPOZICIJA_DIR'])
else:
    PROJECT_DIR = pathlib.Path().resolve()

with (PROJECT_DIR / 'settings.json').open() as f:
    print(PROJECT_DIR / 'settings.json')
    config = json.load(f)

INSTALLED_APPS = ()


# Django autocomplete light
# https://django-autocomplete-light.readthedocs.io/

# django-autocomplete-light have be installed before django.contrib.admin
INSTALLED_APPS += (
    'dal',
    'dal_select2',
)


# Django base settings
# https://docs.djangoproject.com/en/stable/ref/settings/

DEBUG = False
ROOT_URLCONF = 'manopozicija.urls'
SECRET_KEY = config['secret_key']
MEDIA_URL = '/media/'
MEDIA_ROOT = str(PROJECT_DIR / 'var/www/media')
STATIC_URL = '/static/'
STATIC_ROOT = str(PROJECT_DIR / 'var/www/static')
LANGUAGE_CODE = 'lt'
USE_L10N = True

INSTALLED_APPS += (
    'django.contrib.staticfiles',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.auth',
    'django.contrib.messages',
    'django.contrib.admin',
)

MIDDLEWARE = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

_TEMPLATE_CONTEXT_PROCESSORS = [
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
]
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': _TEMPLATE_CONTEXT_PROCESSORS,
        }
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'manopozicija',
    }
}

MIGRATION_MODULES = {
    'openid': 'manopozicija.migrations.openid',
    'account': 'manopozicija.migrations.account',
    'manopozicija': 'manopozicija.migrations.manopozicija',
    'socialaccount': 'manopozicija.migrations.socialaccount',
    'thumbnail': 'manopozicija.migrations.sorlthumbnail',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)-8s %(name)s:%(lineno)d in %(funcName)s [%(threadName)s]: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        }
    },
    'handlers': {
        'stdout': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'loggers': {
        'django': {
            'propagate': True,
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['stdout'],
    }
}


# Static assets, see config/assets.cfg
# https://pypi.python.org/pypi/hexagonit.recipe.download

STATICFILES_DIRS = (
    str(PROJECT_DIR / 'parts/jquery'),
    str(PROJECT_DIR / 'parts/bootstrap'),
    str(PROJECT_DIR / 'parts/requirejs'),
    str(PROJECT_DIR / 'parts/d3'),
)


# django-ompressor settings
# https://pypi.python.org/pypi/django_compressor

INSTALLED_APPS += ('compressor',)
STATICFILES_FINDERS += ('compressor.finders.CompressorFinder',)

COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)


# django-debug-toolbar settings
# https://django-debug-toolbar.readthedocs.org/

INSTALLED_APPS += (
    'debug_toolbar',
)


# django-extensions
# http://django-extensions.readthedocs.org/

INSTALLED_APPS += (
    'django_extensions',
)


# App settings

SERVER_PROTOCOL = 'http://'
SERVER_NAME = 'manoseimas.pylab.lt'

SERVER_ALIASES = (
    'manoseimas.pylab.lt',
    'localhost',
    '127.0.0.1',
)

INSTALLED_APPS += (
    'manopozicija',
)

MANOPOZICIJA_TOPIC_LOGO_SIZE = Size(256, 200)


# django-allauth
# http://django-allauth.readthedocs.org/

SITE_ID = 1
LOGIN_REDIRECT_URL = '/'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_AUTHENTICATION_METHOD = 'email'

AUTHENTICATION_BACKENDS = (
    'allauth.account.auth_backends.AuthenticationBackend',
)

_TEMPLATE_CONTEXT_PROCESSORS += [
    'django.template.context_processors.request',
]

INSTALLED_APPS += (
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.openid',
)

SORTED_AUTH_PROVIDERS = (
    # ('persona', STATIC_URL + 'auth/persona.png'),
    ('google', STATIC_URL + 'auth/google.png'),
    # ('openid.yahoo', STATIC_URL + 'auth/yahoo.png'),
    ('facebook', STATIC_URL + 'auth/facebook.png'),
    ('linkedin', STATIC_URL + 'auth/linkedin.png'),
    ('twitter', STATIC_URL + 'auth/twitter.png'),
    # ('github', STATIC_URL + 'auth/github.png'),
)


# django-bootstrap-form
# https://github.com/tzangms/django-bootstrap-form

INSTALLED_APPS += (
    'bootstrapform',
)


# sorl-thumbnail
# https://github.com/mariocesar/sorl-thumbnail

INSTALLED_APPS += (
    'sorl.thumbnail',
)

THUMBNAIL_ENGINE = 'manopozicija.thumbnails.Engine'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': str(PROJECT_DIR / 'var/cache'),
    }
}

# django-js-reverse
# https://github.com/ierror/django-js-reverse

INSTALLED_APPS += (
    'django_js_reverse',
)

JS_REVERSE_JS_VAR_NAME = 'urls'
JS_REVERSE_JS_GLOBAL_OBJECT_NAME = 'manopozicija'
JS_REVERSE_INCLUDE_ONLY_NAMESPACES = ['js']
JS_REVERSE_JS_MINIFY = False
