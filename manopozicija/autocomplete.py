from dal import autocomplete
from sorl.thumbnail import get_thumbnail

from django.db.models import IntegerField
from django.db.models import Q, Case, When

from manopozicija import models


class Person(autocomplete.Select2QuerySetView):

    def get_result_label(self, item):
        if item.photo:
            im = get_thumbnail(item.photo, '40x40', crop="50% 0%", background="#FFF")
            return '<img src="%s" /> %s' % (im.url, item)
        else:
            return str(item)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.q:
                q = Q(first_name__istartswith=self.q) | Q(last_name__istartswith=self.q)
            else:
                q = Q()
            return (
                models.Actor.objects.
                annotate(hasphoto=Case(When(photo='', then=1), default=0, output_field=IntegerField())).
                filter(q).
                order_by('hasphoto', 'last_name', 'first_name')
            )
        else:
            return models.Actor.objects.none()
