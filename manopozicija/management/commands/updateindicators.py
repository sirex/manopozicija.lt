from django.core.management.base import BaseCommand

from manopozicija import indicators


class Command(BaseCommand):
    help = 'Parses Lithuanian names from vardai.vlkk.lt and writes to specified output file.'

    def _info(self, verbosity, message):
        if verbosity > 0:
            self.stdout.write(message)

    def handle(self, *args, **options):
        self._info(options['verbosity'], 'Importing indicators...')
        indicators.import_indicators(indicators.INDICATORS)

        self._info(options['verbosity'], 'Updating indicators...')
        indicators.update_indicators(indicators.INDICATORS)
