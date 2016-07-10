import pkg_resources as pres

import django.test

from manopozicija.website.parsers.votings import parse_votes
from manopozicija.website.services.voting import import_votes, update_voting, create_vote_positions
from manopozicija.website.models import Actor, Topic, Timeline


class ImportVotesTests(django.test.TestCase):

    def test_import_votes(self):
        url = 'http://www3.lrs.lt/pls/inter/w5_sale.bals?p_bals_id=18573'
        html = pres.resource_string('manopozicija.website.tests', 'fixtures/bals18573.html')
        result = parse_votes(url, html)

        voting = Voting()
        update_voting(voting, result)
        voting.save()

        import_votes(voting, result['table'])
        self.assertEqual(len(result['table']), voting.vote_set.count())
        self.assertEqual(len(result['table']), Person.objects.filter(vote__voting=voting).count())

    def test_create_vote_positions(self):
        topic = Topic.objects.create(title='Balsavimas internetu')
        voting = Voting.objects.create()

        Vote.objects.create(voting=voting, vote=Vote.AYE)
        Vote.objects.create(voting=voting, vote=Vote.ABSTAIN)
        Vote.objects.create(voting=voting, vote=Vote.NO)

        create_vote_positions(topic, voting, weight=-1)

        weights = Position.objects.filter(vote__voting=voting).order_by('pk').values_list('weight', flat=True)
        self.assertEqual(list(weights), [-2, 1, 2])
