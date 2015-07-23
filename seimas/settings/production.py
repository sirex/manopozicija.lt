# pylint: disable=wildcard-import,unused-wildcard-import

from seimas.settings.base import *  # noqa

DEBUG = False

ALLOWED_HOSTS = ['manoseimas.lpylab.lt', 'localhost']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'seimas',
        'USER': 'seimas',
    }
}

LOGGING['root'] = {
    'level': 'WARNING',
    'handlers': ['stdout'],
}

SOCIALACCOUNT_PROVIDERS['persona']['AUDIENCE'] = 'manoseimas.pylab.lt'
