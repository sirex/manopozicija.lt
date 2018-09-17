"""
For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

from django.core.wsgi import get_wsgi_application

from manopozicija.utils.scripting import set_up_environment

set_up_environment()

application = get_wsgi_application()
