from django.core.urlresolvers import reverse


class Item(object):
    def __init__(self, label, name, *args, **kwargs):
        self.label = label
        self.name = name
        self.args = args
        self.kwargs = kwargs

    def url(self):
        return reverse(self.name, args=self.args, kwargs=self.kwargs)


menus = {
    'topmenu': [],
}
