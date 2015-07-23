from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


class Item(object):
    def __init__(self, label, name, *args, **kwargs):
        self.label = label
        self.name = name
        self.args = args
        self.kwargs = kwargs

    def url(self):
        return reverse(self.name, args=self.args, kwargs=self.kwargs)


menus = {
    'topmenu': [
        Item(_('Seimo pozicija'), 'topic-list'),
    ],
}
