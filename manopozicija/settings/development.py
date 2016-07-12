# pylint: disable=wildcard-import,unused-wildcard-import

from manopozicija.settings.base import *  # noqa

DEBUG = True
THUMBNAIL_DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
