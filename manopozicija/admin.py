import uuid
import os.path
import pandas as pd
import posixpath
import panavatar

from django.conf import settings
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.core.files.base import ContentFile

from sorl.thumbnail.admin import AdminImageMixin

from manopozicija import models


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
    raw_id_fields = ('default_body', 'indicators')

    def save_model(self, request, obj, form, change):
        if not obj.logo:
            width, height = settings.MANOPOZICIJA_TOPIC_LOGO_SIZE
            content = ContentFile(panavatar.get_svg(width, height))
            obj.logo.save('%s.svg' % uuid.uuid4(), content)
        obj.save()


class ActorAdmin(AdminImageMixin, admin.ModelAdmin):
    pass


admin.site.register(models.Indicator, IndicatorAdmin)
admin.site.register(models.Topic, TopicAdmin)
admin.site.register(models.Body)
admin.site.register(models.Actor, ActorAdmin)
admin.site.register(models.Post)
admin.site.register(models.TopicCurator)
admin.site.register(models.PostArgument)
admin.site.register(models.Quote)
admin.site.register(models.Group)
admin.site.register(models.Argument)
admin.site.register(models.ActorArgumentPosition)
# admin.site.register(Post
