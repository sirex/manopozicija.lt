import yaml
import pathlib
import unidecode
import collections

from django.core.management.base import BaseCommand
from django.core.files import File

from manopozicija import models
from manopozicija import helpers


class Command(BaseCommand):
    help = 'Import photos of public people from variuos sources.'

    def add_arguments(self, parser):
        parser.add_argument('path', help="Path to the photos YAML file")
        parser.add_argument('base', help="Path to the directory where photos are saved")

    def handle(self, path, base, **options):
        printer = helpers.Printer(self.stdout, options['verbosity'])
        path = pathlib.Path(path)
        base = pathlib.Path(base)

        with path.open() as f:
            photos = yaml.safe_load(f)

        def clean_name(name):
            return unidecode.unidecode(name).lower()

        Person = collections.namedtuple('Person', 'id first_name last_name birth_date')
        names = collections.defaultdict(list)
        for x in models.Actor.objects.filter(birth_date__isnull=False, group=False):
            names[clean_name(x.first_name + ' ' + x.last_name)].append(Person(
                id=x.id,
                first_name=x.first_name,
                last_name=x.last_name,
                birth_date=x.birth_date,
            ))

        for photo in photos:
            cleaned_name = clean_name(photo['name'])
            if cleaned_name in names:
                matches = [
                    x for x in names[cleaned_name] if (
                        photo.get('born') is None or
                        photo['born'].strftime('%Y-%m-%d') == x.birth_date.strftime('%Y-%m-%d')
                    )
                ]

                if len(matches) == 1:
                    x = matches[0]
                    printer.info('- name: %s %s' % (x.first_name, x.last_name))
                    printer.info('  born: %s' % (x.birth_date.strftime('%Y-%m-%d')))
                    printer.info('  photo: %s' % photo['photo'])

                    photo_path = (base / photo['photo']) if photo['photo'] else None
                    if photo_path and photo_path.exists():
                        actor = models.Actor.objects.get(pk=x.id)
                        if not actor.photo:
                            with photo_path.open('rb') as f:
                                actor.photo.save(path.name, File(f), save=True)
                    elif photo_path:
                        printer.info("  error: logo %r can't be found" % photo['photo'])
                else:
                    printer.info('# edit: multiple matches')
                    for x in matches:
                        printer.info('- name: %s %s' % (x.first_name, x.last_name))
                        printer.info('  born: %s' % (x.birth_date.strftime('%Y-%m-%d')))
                        printer.info('  photo: %s' % photo['photo'])
            else:
                printer.info('# edit: no match found')
                printer.info('- name: %s' % photo['name'])
                printer.info('  photo: %s' % photo['photo'])
