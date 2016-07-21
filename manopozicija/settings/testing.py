# pylint: disable=wildcard-import,unused-wildcard-import

from manopozicija.settings.base import *  # noqa

SERVER_PROTOCOL = 'http://'
SERVER_NAME = 'localhost:80'

LOGGING['loggers']['factory'] = {
    'level': 'DEBUG',
    'handlers': ['stdout'],
}
