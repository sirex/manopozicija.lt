from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from manopozicija import views
from manopozicija import autocomplete

pk = r'<int:object_id>'
slug = r'<int:object_id>/<slug:slug>'

urlpatterns = [
    path('', views.topic_list, name='topic-list'),
    path('naujas-asmuo/', views.person_form, name='person-create'),
    path('nauja-grupe/', views.group_form, name='group-create'),
    path('temos/%s/nauja-citata/' % slug, views.quote_form, name='quote-create'),
    path('citatos/%s/keisti/' % pk, views.quote_update_form, name='quote-update'),
    path('irasai/%s/trinti/' % pk, views.post_delete, name='post-delete'),
    path('temos/%s/naujas-ivykis/' % slug, views.event_form, name='event-create'),
    path('temos/%s/naujas-kuratorius/' % slug, views.curator_form, name='curator-apply'),
    path('temos/%s/' % slug, views.topic_details, name='topic-details'),
    path('temos/%s/kpi/' % slug, views.topic_kpi, name='topic-kpi'),
    path('palyginimas/%s/' % slug, views.compare_positions, name='compare-positions'),
    path('autocomplete/actor/', autocomplete.Person.as_view(), name='autocomplete-actor'),
    path('', include(([
        path('naudotojo-balsas/<int:post_id>/', views.user_post_vote, name='user-post-vote'),
        path('kuratoriaus-balsas/<int:post_id>/', views.curator_post_vote, name='curator-post-vote'),
    ], 'js'))),
]

urlpatterns += [
    path('accounts/', include('allauth.urls')),
    path('valdymas/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
