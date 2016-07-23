from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

from manopozicija import views

slug = r'(?P<object_id>\d+)/(?P<slug>[a-z0-9-]+)'

urlpatterns = [
    url(r'^$', views.topic_list, name='topic-list'),
    url(r'^naujas-asmuo/$', views.person_form, name='person-create'),
    url(r'^nauja-grupe/$', views.group_form, name='group-create'),
    url(r'^temos/%s/nauja-citata/$' % slug, views.quote_form, name='quote-create'),
    url(r'^temos/%s/naujas-ivykis/$' % slug, views.event_form, name='event-create'),
    url(r'^temos/%s/naujas-kuratorius/$' % slug, views.curator_form, name='curator-apply'),
    url(r'^temos/%s/$' % slug, views.topic_details, name='topic-details'),
    url(r'^temos/%s/kpi/$' % slug, views.topic_kpi, name='topic-kpi'),
    url(r'^palyginimas/%s/$' % slug, views.compare_positions, name='compare-positions'),
    url(r'', include([
        url(r'^naudotojo-balsas/(?P<post_id>\d+)/$', views.user_post_vote, name='user-post-vote'),
        url(r'^kuratoriaus-balsas/(?P<post_id>\d+)/$', views.curator_post_vote, name='curator-post-vote'),
    ], namespace='js')),
]

urlpatterns += [
    url(r'^accounts/', include('allauth.urls')),
    url(r'^valdymas/', include(admin.site.urls)),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
