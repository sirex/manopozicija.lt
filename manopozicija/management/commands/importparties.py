import yaml
import pathlib

from django.core.management.base import BaseCommand
from django.core.files import File

from manopozicija import models
from manopozicija import helpers


class Command(BaseCommand):
    help = 'Import political parties together with photos'

    def add_arguments(self, parser):
        parser.add_argument('path', help="Path to the parties file")

    def handle(self, path, **options):
        path = pathlib.Path(path)
        base = path.parent
        printer = helpers.Printer(self.stdout, options['verbosity'])

        printer.info("Importing political parties...")
        with path.open() as f:
            parties = yaml.safe_load(f)

        for party in parties:
            printer.info('  %s' % party['name'])

            names = [party['name']] + party.get('alternate_names', [])
            try:
                actor = models.Actor.objects.get(first_name__in=names, group=True)
            except models.Actor.DoesNotExist:
                printer.info((
                    "    error: can't find existing party entry in database with Actor.first_name=%r."
                ) % party['name'])
            else:
                logo = (base / party['logo']) if party['logo'] else None
                if logo and logo.exists():
                    if not actor.photo:
                        with logo.open('rb') as f:
                            actor.photo.save(path.name, File(f), save=True)
                elif logo:
                    printer.info("    error: logo %r can't be found" % party['logo'])

        printer.info("done.")
