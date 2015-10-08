# pylint: disable=wildcard-import,unused-wildcard-import

from seimas.settings.base import *  # noqa

DEBUG = False

ALLOWED_HOSTS = ['manopozicija.lt', 'meras.lt', 'localhost']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'manopozicija',
        'USER': 'manopozicija',
    }
}

LOGGING['root'] = {
    'level': 'WARNING',
    'handlers': ['stdout'],
}

SOCIALACCOUNT_PROVIDERS['persona']['AUDIENCE'] = 'manoseimas.pylab.lt'
