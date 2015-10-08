from django_webtest import WebTest

from django.contrib.auth.models import User

from seimas.website.models import Topic
from seimas.website.models import Voting
from seimas.website.models import Position


class ViewTests(WebTest):

    def test_topic_list(self):
        Topic.objects.create(title='Balsavimas internetu')

        resp = self.app.get('/')
        self.assertEqual(resp.status_int, 200)
        resp.mustcontain('Balsavimas internetu')

    def test_topic_details(self):
        topic = Topic.objects.create(title='Balsavimas internetu')
        voting = Voting.objects.create(title='Balsavimo internetu koncepcijos patvirtinimas')
        Position.objects.create(topic=topic, content_object=voting, weight=1)

        resp = self.app.get('/temos/balsavimas-internetu/')
        self.assertEqual(resp.status_int, 200)
        resp.mustcontain('Balsavimo internetu koncepcijos patvirtinimas')

    def test_topic_form(self):
        user = User.objects.create_user('user', 'user@example.com', 'secret')

        resp = self.app.get('/temos/nauja-tema/', user='user')
        resp.form['title'] = 'Darželių problema'
        resp.form['description'] = 'Darželių problema.'
        resp = resp.form.submit()

        topic = Topic.objects.get(slug='darzeliu-problema')
        self.assertEqual(topic.author, user)


class ImportVotesTests(WebTest):

    def test_import_votes(self):
        user = User.objects.create_superuser('admin', 'admin@example.com', 'secret')
        topic = Topic.objects.create(title='Balsavimas internetu')

        self.assertEqual(Voting.objects.count(), 0)

        resp = self.app.get('/temos/balsavimas-internetu/add-voting/', user='admin')
        resp.form['title'] = 'Balsavimo internetu koncepcijos patvirtinimas'
        resp.form['link'] = 'http://www3.lrs.lt/pls/inter/w5_sale.bals?p_bals_id=18573'
        resp.form['weight'] = '3'
        resp = resp.form.submit()

        self.assertEqual(resp.status_int, 302)
        self.assertEqual(Voting.objects.count(), 1)

        voting = Voting.objects.get()

        self.assertEqual(voting.author.pk, user.pk)
        self.assertEqual(voting.vid, '18573')
        self.assertEqual(voting.vote_set.count(), 141)
        self.assertEqual(Position.objects.get(topic=topic, voting=voting).weight, 3)

    def test_submit_existing_voting(self):
        User.objects.create_superuser('admin', 'admin@example.com', 'secret')
        topic = Topic.objects.create(title='Balsavimas internetu')
        voting = Voting.objects.create(
            title='Balsavimo internetu koncepcijos patvirtinimas',
            vid='18573',
            link='http://www3.lrs.lt/pls/inter/w5_sale.bals?p_bals_id=18573',
        )
        Position.objects.create(topic=topic, content_object=voting, weight=1)

        self.assertEqual(Voting.objects.count(), 1)

        resp = self.app.get('/temos/balsavimas-internetu/add-voting/', user='admin')
        resp.form['title'] = 'Balsavimo internetu koncepcijos patvirtinimas'
        resp.form['link'] = 'http://www3.lrs.lt/pls/inter/w5_sale.bals?p_bals_id=18573'
        resp = resp.form.submit()

        self.assertEqual(resp.status_int, 200)
        self.assertEqual(Voting.objects.count(), 1)
