import uuid
import os.path
import requests
import urllib.parse
import pandas as pd
import posixpath
import panavatar

import django.contrib.auth.models as auth_models
import django.contrib.auth.admin as auth_admin
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.views import redirect_to_login
from django.contrib.sites.models import Site
from django.contrib.sites.admin import SiteAdmin
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.core.files.base import ContentFile

import allauth.socialaccount.admin as allauth

import seimas.website.models as website_models

from seimas.website.parsers.votings import parse_votes
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


class IndicatorAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'last_update',
        'error_count',
    )
    readonly_fields = (
        'created',
        'modified',
        'deleted',
        'last_update',
        'error_count',
        'traceback',
        'indicator_file',
        'indicator_preview',
    )

    def indicator_file(self, instance):
        if instance.slug:
            file_url = posixpath.join(settings.MEDIA_URL, 'indicators', '%s.csv' % instance.slug)
            return mark_safe('<a href="%s" target="_blank">%s</a>' % (file_url, file_url))

    def indicator_preview(self, instance):
        if instance.slug:
            indicators_dir = os.path.join(settings.MEDIA_ROOT, 'indicators')
            frame = pd.read_csv(os.path.join(indicators_dir, '%s.csv' % instance.slug))
            return mark_safe('<div style="float:left;">%s</div>' % ''.join(frame.head(10).to_html().splitlines()))

    indicator_preview.short_description = _('Indicator preview')


class TopicAdmin(admin.ModelAdmin):
    raw_id_fields = ('author', 'indicators')

    def save_model(self, request, obj, form, change):
        if not obj.logo:
            width, height = 256, 200
            content = ContentFile(panavatar.get_svg(width, height))
            obj.logo.save('%s.svg' % uuid.uuid4(), content)
        obj.save()


site = AdminSite()

site.register(auth_models.User, auth_admin.UserAdmin)
site.register(website_models.Indicator, IndicatorAdmin)
site.register(website_models.Topic, TopicAdmin)
site.register(website_models.Position)
site.register(website_models.Voting, VotingAdmin)
site.register(website_models.Vote)

site.register(allauth.SocialApp, allauth.SocialAppAdmin)
site.register(allauth.SocialToken, allauth.SocialTokenAdmin)
site.register(allauth.SocialAccount, allauth.SocialAccountAdmin)

site.register(Site, SiteAdmin)
