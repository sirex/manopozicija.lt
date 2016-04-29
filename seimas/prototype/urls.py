from django.conf.urls import url

from seimas.prototype.views import prototype
from seimas.prototype.helpers import get_urls


urlpatterns = [
    url(r'^$', prototype, {'path': ''}, name='prototype'),
    url(r'^(?P<path>.*?)/$', prototype, name='prototype'),
] + get_urls(prototype)
