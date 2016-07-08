# pylint: disable=wildcard-import,unused-wildcard-import

from seimas.settings.base import *  # noqa

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'seimas.db',
    }
}
