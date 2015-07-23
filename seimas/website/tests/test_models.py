import pkg_resources as pres

import django.test

from seimas.website.parsers import parse_votes
from seimas.website.services import import_votes, update_voting
from seimas.website.models import Voting


class ImportVotesTests(django.test.TestCase):

    def test_import_votes(self):
        url = 'http://www3.lrs.lt/pls/inter/w5_sale.bals?p_bals_id=18573'
        html = pres.resource_string('seimas.website.tests', 'fixtures/bals18573.html')
        result = parse_votes(url, html)

        voting = Voting()
        update_voting(voting, result)
        voting.save()

        import_votes(voting, result['table'])
        self.assertEqual(len(result['table']), voting.vote_set.count())
