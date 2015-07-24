import argparse
import requests

from django.core.management.base import BaseCommand

from seimas.website.parsers.names import parse_index, parse_names


class Command(BaseCommand):
    help = 'Parses Lithuanian names from vardai.vlkk.lt and writes to specified output file.'

    def add_arguments(self, parser):
        parser.add_argument('output', type=argparse.FileType('w', encoding='UTF-8'))

    def handle(self, *args, **options):
        output = options['output']
        resp = requests.get('http://vardai.vlkk.lt/')
        for link in parse_index(resp.content):
            for sex, name in parse_names(requests.get(link).content):
                output.write('%s\t%s\n' % (sex, name))
