import io
import json
import base64
import pathlib
import unidecode
import collections

from django.core.management.base import BaseCommand
from django.core.files import File

from manopozicija import models
from manopozicija import helpers


def clean_name(name):
    name = ' '.join(name.strip().split())
    return unidecode.unidecode(name).lower()


class Command(BaseCommand):
    """

    .ndjson file should contain this structure:

        [<first name>, <last name>, <birth date>, <photo file extension>, <base64 encoded photo>]

    """

    help = 'Import photos from ndjson file.'

    def add_arguments(self, parser):
        parser.add_argument('path', help="Path to the NDJSON file containing photos")

    def handle(self, path, **options):
        printer = helpers.Printer(self.stdout, options['verbosity'])
        path = pathlib.Path(path)

        # Get existing actors from database
        Person = collections.namedtuple('Person', 'id fname lname bdate')
        names = collections.defaultdict(list)
        for x in models.Actor.objects.filter(birth_date__isnull=False, group=False):
            key = clean_name(x.first_name + ' ' + x.last_name) + ' ' + x.birth_date.strftime('%Y-%m-%d')
            names[key].append(Person(
                id=x.id,
                fname=x.first_name,
                lname=x.last_name,
                bdate=x.birth_date,
            ))

        # Update photos
        with path.open(encoding='utf-8') as f:
            for line in f:
                fname, lname, bdate, ext, data = json.loads(line)
                key = clean_name(fname + ' ' + lname) + ' ' + bdate
                printer.info('- name: %s %s (%s)' % (fname, lname, bdate))

                found = len(names[key]) if key in names else 0
                if found == 1:
                    x = names[key][0]
                    actor = models.Actor.objects.get(pk=x.id)
                    if actor.photo:
                        printer.info('  info, not updating: %s %s (%s)' % (fname, lname, bdate))
                    else:
                        filename = '%s-%s.%s' % (fname, lname, ext)
                        content = base64.b64decode(data.encode('ascii'))
                        content = io.BytesIO(content)
                        actor.photo.save(filename, File(content), save=True)
                elif found > 1:
                    printer.info('  error, multiple matches found: %s %s (%s)' % (fname, lname, bdate))
                else:
                    printer.info('  error, no match found: %s %s (%s)' % (fname, lname, bdate))
