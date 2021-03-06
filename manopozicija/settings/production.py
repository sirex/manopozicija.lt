# pylint: disable=wildcard-import,unused-wildcard-import

from manopozicija.settings.base import *  # noqa

DEBUG = False

ALLOWED_HOSTS = ['manopozicija.lt', 'localhost']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'manopozicija',
    }
}

LOGGING['root'] = {  # noqa
    'level': 'WARNING',
    'handlers': ['stdout'],
}

INSTALLED_APPS += (  # noqa
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.github',
)

SOCIALACCOUNT_PROVIDERS = {
    'openid': {},
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    },
    'facebook': {
        'SCOPE': ['email', 'public_profile'],
        'METHOD': 'oauth2',
        'VERIFIED_EMAIL': False,
        'VERSION': 'v2.4',
    },
    'github': {
        'SCOPE': ['user:email'],
    },
}
