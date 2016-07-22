import yaml

from django.core.management.base import BaseCommand

from manopozicija import forms
from manopozicija import models
from manopozicija import services


class Printer(object):

    def __init__(self, stdout, verbosity):
        self.stdout = stdout
        self.verbosity = verbosity

    def info(self, msg):
        if self.verbosity > 0:
            self.stdout.write(msg)


class Command(BaseCommand):
    help = 'Imports posts to an existing topic'

    def add_arguments(self, parser):
        parser.add_argument('slug', help="topic slug")
        parser.add_argument('path', help="YAML file with topic posts")

    def handle(self, slug, path, **options):
        printer = Printer(self.stdout, options['verbosity'])
        user = services.get_bot_user('importbot')
        topic = models.Topic.objects.get(slug=slug)
        with open(path) as f:
            posts = yaml.safe_load(f)

        for post in posts:
            if post['type'] == 'event':
                exists = (
                    models.Event.objects.
                    filter(post__topic=topic, source_link=post['event']['source_link']).
                    exists()
                )
                if exists:
                    printer.info('"%s" already exists.' % post['event']['title'])
                else:
                    form = forms.EventForm(topic, post['event'])
                    if form.is_valid():
                        services.create_event(user, topic, form.cleaned_data)
                        printer.info('"%s" imported.' % post['event']['title'])
                    else:
                        printer.info('Error while importing %r' % post['event'])
                        printer.info(form.errors.as_text())
