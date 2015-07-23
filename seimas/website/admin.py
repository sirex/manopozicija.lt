import requests
import urllib.parse

import django.contrib.auth.models as auth_models
import django.contrib.auth.admin as auth_admin
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.views import redirect_to_login

import allauth.socialaccount.admin as allauth

import seimas.website.models as website_models

from seimas.website.parsers import parse_votes
from seimas.website.services.voting import update_voting
from seimas.website.services.voting import import_votes


class AdminSite(admin.AdminSite):

    def _is_login_redirect(self, response):
        if isinstance(response, HttpResponseRedirect):
            login_url = reverse('admin:login', current_app=self.name)
            response_url = urllib.parse.urlparse(response.url).path
            return login_url == response_url
        else:
            return False

    def admin_view(self, view, cacheable=False):
        inner = super().admin_view(view, cacheable)

        def wrapper(request, *args, **kwargs):
            response = inner(request, *args, **kwargs)
            if self._is_login_redirect(response):
                if request.user.is_authenticated():
                    return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
                else:
                    return redirect_to_login(request.get_full_path(), reverse('accounts_login'))
            else:
                return response

        return wrapper


class VotingAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        data = None

        if not obj.author:
            obj.author = request.user

        if not obj.vid:
            resp = requests.get(obj.link)
            data = parse_votes(obj.link, resp.content)
            update_voting(obj, data)

        obj.save()

        if data:
            import_votes(obj, data['table'])


site = AdminSite()

site.register(auth_models.User, auth_admin.UserAdmin)
site.register(website_models.Topic)
site.register(website_models.Position)
site.register(website_models.Voting, VotingAdmin)
site.register(website_models.Vote)

site.register(allauth.SocialApp, allauth.SocialAppAdmin)
site.register(allauth.SocialToken, allauth.SocialTokenAdmin)
site.register(allauth.SocialAccount, allauth.SocialAccountAdmin)
