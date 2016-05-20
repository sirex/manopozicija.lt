import importlib

from django.conf.urls import url, include

import allauth.socialaccount.providers as allauth_providers

import seimas.accounts.views as accounts_views


def get_provider_urls(provider):  # pylint: disable=redefined-outer-name
    try:
        urls = importlib.import_module(provider.get_package() + '.urls')
    except ImportError:
        return []
    else:
        return getattr(urls, 'urlpatterns', [])


urlpatterns = [
    url(r'^login/$', accounts_views.login, name='accounts_login'),
    url(r'^logout/$', accounts_views.logout, name='accounts_logout'),
    url(r'^logout/$', accounts_views.logout, name='account_logout'),  # django-allauth requires this url name
    url(r'^settings/$', accounts_views.settings, name='accounts_settings'),
    url(r'', include('allauth.socialaccount.urls')),
]

for provider in allauth_providers.registry.get_list():
    urlpatterns += get_provider_urls(provider)
