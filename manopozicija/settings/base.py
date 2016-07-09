import exportrecipe
import pathlib
import collections

Size = collections.namedtuple('Size', ['width', 'height'])

PROJECT_DIR = pathlib.Path(__file__).parents[2]

config = exportrecipe.load(str(PROJECT_DIR / 'settings.json'))


# Django base settings
# https://docs.djangoproject.com/en/stable/ref/settings/

DEBUG = False
ROOT_URLCONF = 'manopozicija.website.urls'
SECRET_KEY = config.secret_key
MEDIA_URL = '/media/'
MEDIA_ROOT = str(PROJECT_DIR / 'var/www/media')
STATIC_URL = '/static/'
STATIC_ROOT = str(PROJECT_DIR / 'var/www/static')
LANGUAGE_CODE = 'lt'
USE_L10N = True

INSTALLED_APPS = (
    'django.contrib.staticfiles',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.auth',
    'django.contrib.messages',
    'django.contrib.admin',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

_TEMPLATE_CONTEXT_PROCESSORS = [
    'django.contrib.auth.context_processors.auth',
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
        'NAME': 'seimas',
    }
}

MIGRATION_MODULES = {
    'account': 'manopozicija.website.migrations.account',
    'website': 'manopozicija.website.migrations.website',
    'openid': 'manopozicija.website.migrations.openid',
    'socialaccount': 'manopozicija.website.migrations.socialaccount',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'stdout': {
            'format': (
                '%(levelname)s %(asctime)s %(module)s '
                '%(process)d %(thread)d %(message)s'
            ),
        },
        'console': {
            'format': '%(levelname)s %(module)s %(message)s',
        },
    },
    'handlers': {
        'stdout': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'stdout',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
    },
    'loggers': {
        'django': {
            'propagate': True,
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console'],
    }
}


# Static assets, see config/assets.cfg
# https://pypi.python.org/pypi/hexagonit.recipe.download

STATICFILES_DIRS = (
    str(PROJECT_DIR / 'parts/jquery'),
    str(PROJECT_DIR / 'parts/bootstrap'),
    str(PROJECT_DIR / 'parts/requirejs'),
    str(PROJECT_DIR / 'parts/c3'),
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


# django-nose
# https://pypi.python.org/pypi/django-nose

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

INSTALLED_APPS += (
    'django_nose',
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
    'manopozicija.website',
    'manopozicija.prototype',
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
    ('persona', STATIC_URL + 'auth/persona.png'),
    ('google', STATIC_URL + 'auth/google.png'),
    ('openid.yahoo', STATIC_URL + 'auth/yahoo.png'),
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