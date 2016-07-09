import os
import pkg_resources as pres


def reload_server():
    os.utime(pres.resource_filename('prototype', 'main.py'), None)


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "prototype.settings")

    from django.core.wsgi import get_wsgi_application
    from livereload import Server, shell

    application = get_wsgi_application()
    server = Server(application)
    server.watch('prototype.yml', reload_server)
    server.watch('templates/')
    server.watch('styles/', shell(['sassc', 'styles/main.scss', 'static/css/main.css']))
    server.serve(port=8000)
