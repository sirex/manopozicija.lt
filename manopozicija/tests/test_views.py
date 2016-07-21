from webtest import Upload

from django.core.urlresolvers import reverse

from manopozicija import models
from manopozicija import services
from manopozicija import factories


def test_create_person(app):
    factories.UserFactory()

    resp = app.get(reverse('person-create'), user='vardenis')
    form = resp.forms['person-form']
    form['first_name'] = 'Mantas'
    form['last_name'] = 'Adomėnas'
    form['title'] = 'seimo narys'
    resp = form.submit()

    assert resp.headers['location'] == '/'
    assert models.Actor.objects.filter(first_name='Mantas', last_name='Adomėnas').exists()


def test_create_group(app):
    factories.UserFactory()

    resp = app.get(reverse('group-create'), user='vardenis')
    form = resp.forms['group-form']
    form['first_name'] = 'Lietuvos Žaliųjų Partija'
    form['title'] = 'politinė partija'
    resp = form.submit()

    assert resp.headers['location'] == '/'
    assert models.Actor.objects.filter(first_name='Lietuvos Žaliųjų Partija').exists()


def test_create_event(app):
    user = factories.UserFactory()
    topic = factories.TopicFactory()
    factories.TopicCuratorFactory(user=user, topic=topic)

    resp = app.get(reverse('event-create', args=[topic.pk, topic.slug]), user=user)
    form = resp.forms['event-form']
    form['title'] = 'Balsavimo internetu koncepcijos patvirtinimas'
    form['source_link'] = 'https://e-seimas.lrs.lt/portal/legalAct/lt/TAD/TAIS.287235?positionInSearchResults=0&searchModelUUID=eaee1625-cf9f-46c0-931c-482a218029e8'
    form['timestamp'] = '2006-11-16'
    resp = form.submit()

    assert resp.status == '302 Found'
    assert resp.headers['location'] == topic.get_absolute_url()
    assert services.dump_topic_posts(topic) == '\n'.join([
        ' o  (-) Balsavimo internetu koncepcijos patvirtinimas                         e-seimas.lrs.lt 2006-11-16 (0)',
    ])

    # Try to add same event second time
    resp = app.get(reverse('event-create', args=[topic.pk, topic.slug]), user=user)
    form = resp.forms['event-form']
    form['title'] = 'Balsavimo internetu koncepcijos patvirtinimas'
    form['source_link'] = 'https://e-seimas.lrs.lt/portal/legalAct/lt/TAD/TAIS.287235?positionInSearchResults=0&searchModelUUID=eaee1625-cf9f-46c0-931c-482a218029e8'
    form['timestamp'] = '2006-11-16'
    resp = form.submit()

    assert resp.status == '200 OK'
    assert resp.context['form'].errors.as_text() == '\n'.join([
        '* source_link',
        '  * Toks sprendimas jau yra įtrauktas į „Balsavimas internetu“ temą.',
    ])
    assert services.dump_topic_posts(topic) == '\n'.join([
        ' o  (-) Balsavimo internetu koncepcijos patvirtinimas                         e-seimas.lrs.lt 2006-11-16 (0)',
    ])


def test_create_quote(app):
    # This snippet allows to run tests without running slow migrations
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')

    user = factories.UserFactory()
    actor = factories.PersonActorFactory()
    topic = factories.TopicFactory()
    factories.TopicCuratorFactory(user=user, topic=topic)

    resp = app.get(reverse('quote-create', args=[topic.pk, topic.slug]), user='vardenis')
    form = resp.forms['quote-form']
    form['actor'] = actor.pk
    form['source_link'] = 'http://kauno.diena.lt/naujienos/lietuva/politika/skinasi-kelia-balsavimas-internetu-740017'
    form['timestamp'] = '2016-03-22 16:34'
    form['text'] = 'Nepasiduokime paviršutiniškiems šūkiams – šiuolaikiška, modernu.'
    form['form-0-title'] = 'šiuolaikiška, modernu'
    form['form-0-counterargument'] = True
    resp = form.submit()

    assert resp.status == '302 Found'
    assert resp.headers['location'] == topic.get_absolute_url()
    assert services.dump_topic_posts(topic) == '\n'.join([
        '( ) (n) Mantas Adomėnas (seimo narys)                                          kauno.diena.lt 2016-03-22    ',
        ' |      Nepasiduokime paviršutiniškiems šūkiams – šiuolaikiška, modernu.                                 (0)',
        ' |      - (y) šiuolaikiška, modernu < (counterargument)                                                     ',
    ])

    resp = app.get(reverse('quote-create', args=[topic.pk, topic.slug]), user='vardenis')
    form = resp.forms['quote-form']
    form['actor'] = actor.pk
    form['source_link'] = 'http://kauno.diena.lt/naujienos/lietuva/politika/skinasi-kelia-balsavimas-internetu-740017'
    form['timestamp'] = '2016-03-22 16:34'
    form['text'] = 'Atidaroma galimybė prekiauti balsais ir likti nebaudžiamam.'
    form['form-0-title'] = 'balsų pirkimas'
    form['form-0-position'] = True
    resp = form.submit()

    assert resp.status == '302 Found'
    assert resp.headers['location'] == topic.get_absolute_url()
    assert services.dump_topic_posts(topic) == '\n'.join([
        '( ) (n) Mantas Adomėnas (seimo narys)                                          kauno.diena.lt 2016-03-22    ',
        ' |      Nepasiduokime paviršutiniškiems šūkiams – šiuolaikiška, modernu.                                 (0)',
        ' |      - (y) šiuolaikiška, modernu < (counterargument)                                                     ',
        ' |      Atidaroma galimybė prekiauti balsais ir likti nebaudžiamam.                                      (0)',
        ' |      - (n) balsų pirkimas                                                                                ',
    ])

    # Try to add similar quote from same author and from same source
    resp = app.get(reverse('quote-create', args=[topic.pk, topic.slug]), user='vardenis')
    form = resp.forms['quote-form']
    form['actor'] = actor.pk
    form['source_link'] = 'http://kauno.diena.lt/naujienos/lietuva/politika/skinasi-kelia-balsavimas-internetu-740017'
    form['timestamp'] = '2016-03-22 16:34'
    form['text'] = 'Atidaroma nauja galimybė prekiauti balsais ir likti nebaudžiamam.'
    form['form-0-title'] = 'balsų pirkimas'
    form['form-0-position'] = True
    resp = form.submit()

    assert resp.status == '200 OK'
    assert resp.context['quote_form'].errors.as_text() == '\n'.join([
        '* text',
        '  * Toks komentaras jau yra įtrauktas į „Balsavimas internetu“ temą.',
    ])
    assert services.dump_topic_posts(topic) == '\n'.join([
        '( ) (n) Mantas Adomėnas (seimo narys)                                          kauno.diena.lt 2016-03-22    ',
        ' |      Nepasiduokime paviršutiniškiems šūkiams – šiuolaikiška, modernu.                                 (0)',
        ' |      - (y) šiuolaikiška, modernu < (counterargument)                                                     ',
        ' |      Atidaroma galimybė prekiauti balsais ir likti nebaudžiamam.                                      (0)',
        ' |      - (n) balsų pirkimas                                                                                ',
    ])


def test_curator_apply(app):
    user = factories.UserFactory(
        username='vardenis',
        email='vardenis.pavardenis@example.com',
        first_name='',
        last_name='',
    )
    topic = factories.TopicFactory()

    resp = app.get(reverse('curator-apply', args=[topic.pk, topic.slug]), user=user)
    form = resp.forms['curator-form']
    form['first_name'] = 'Vardenis'
    form['last_name'] = 'Pavardenis'
    form['title'] = 'visuomenės veikėjas'
    form['photo'] = Upload('my.jpg', factories.get_image_bytes())
    resp = form.submit()

    assert resp.status == '302 Found'
    assert resp.headers['location'] == topic.get_absolute_url()
    assert models.Curator.objects.get(user=user).title == 'visuomenės veikėjas'
    assert services.dump_topic_posts(topic) == ''
    assert services.dump_topic_posts(topic, queue=True) == '\n'.join([
        '( ) Vardenis Pavardenis (visuomenės veikėjas)                                naujas temos kuratorius (0)',
    ])

    # A curator steps in and approves curator application
    post = models.Post.objects.order_by('pk').last()
    curator = factories.UserFactory(first_name='kuratorius')
    factories.TopicCuratorFactory(user=curator, topic=topic)
    resp = app.post(reverse('js:curator-post-vote', args=[post.pk]), {'vote': 1}, user=curator)
    assert resp.json == {'success': True, 'upvotes': 1, 'downvotes': 0}
    assert services.dump_topic_posts(topic, queue=True) == ''

    # A new curator user tries to vote for his own curator application
    resp = app.post(reverse('js:curator-post-vote', args=[post.pk]), {'vote': 1}, user=user)
    assert resp.json == {'success': False}
    assert services.dump_topic_posts(topic, queue=True) == ''

    # Another curator steps in and dissagrees with approval
    curator = factories.UserFactory(first_name='kuratorius 2')
    factories.TopicCuratorFactory(user=curator, topic=topic)
    resp = app.post(reverse('js:curator-post-vote', args=[post.pk]), {'vote': -1}, user=curator)
    assert resp.json == {'success': True, 'upvotes': 1, 'downvotes': 1}
    assert services.dump_topic_posts(topic, queue=True) == '\n'.join([
        '( ) Vardenis Pavardenis (visuomenės veikėjas)                                naujas temos kuratorius (-1)',
    ])

    # A not curator user tries to vote for his curator application
    resp = app.post(reverse('js:curator-post-vote', args=[post.pk]), {'vote': 1}, user=user)
    assert resp.json == {'success': False}
    assert services.dump_topic_posts(topic, queue=True) == '\n'.join([
        '( ) Vardenis Pavardenis (visuomenės veikėjas)                                naujas temos kuratorius (-1)',
    ])


def test_user_post_vote(app):
    user = factories.UserFactory()
    topic = factories.TopicFactory()
    event = factories.EventFactory()
    post = factories.PostFactory(topic=topic, content_object=event)

    # User upvotes a post
    resp = app.post(reverse('js:user-post-vote', args=[post.pk]), {'vote': 1}, user=user)
    assert resp.json == {'success': True, 'upvotes': 1, 'downvotes': 0}
    assert services.dump_topic_posts(topic) == '\n'.join([
        ' o  (-) Balsavimo internetu koncepcijos patvirtinimas                         e-seimas.lrs.lt 2016-03-22 (1)',
    ])

    # User downvotes same post
    resp = app.post(reverse('js:user-post-vote', args=[post.pk]), {'vote': -1}, user=user)
    assert resp.json == {'success': True, 'upvotes': 0, 'downvotes': 1}
    assert services.dump_topic_posts(topic) == '\n'.join([
        ' o  (-) Balsavimo internetu koncepcijos patvirtinimas                         e-seimas.lrs.lt 2016-03-22 (-1)',
    ])

    # User clears his vote
    resp = app.post(reverse('js:user-post-vote', args=[post.pk]), {'vote': 0}, user=user)
    assert resp.json == {'success': True, 'upvotes': 0, 'downvotes': 0}
    assert services.dump_topic_posts(topic) == '\n'.join([
        ' o  (-) Balsavimo internetu koncepcijos patvirtinimas                         e-seimas.lrs.lt 2016-03-22 (0)',
    ])


def test_topic_details(app):
    user = factories.UserFactory()
    topic = factories.TopicFactory()
    factories.TopicCuratorFactory(user=user, topic=topic)
    factories.create_topic_posts(topic, user, [
        ('event', 0, 1, 'Balsavimo internetu koncepcijos patvirtinimas', 'lrs.lt', '2006-11-26'),
        ('quote', 'Mantas Adomėnas', 'seimo narys', 'kauno.diena.lt', '2016-03-22', [
            (1, 0, 'Nepasiduokime paviršutiniškiems šūkiams – šiuolaikiška, modernu.', [
                (1, 'šiuolaikiška, modernu', True),
            ]),
            (1, 0, 'Atidaroma galimybė prekiauti balsais ir likti nebaudžiamam.', [
                (-1, 'balsų pirkimas', None),
            ]),
        ]),
        ('quote', 'Eligijus Masiulis', 'seimo narys', 'delfi.lt', '2015-10-08', [
            (0, 0, 'Mes palaikysim tokį įstatymą, nes turime žengti į priekį ir reaguoti į XXI a. iššūkius.', [
                (1, 'šiuolaikiška, modernu', None),
            ]),
        ]),
    ])
    factories.create_topic_posts(topic, None, [('curator', 'Vardenis Pavardenis', 'inžinierius')])

    app.get(reverse('topic-details', args=[topic.pk, topic.slug]), user=user)


def test_compare(app):
    user = factories.UserFactory()
    topic = factories.TopicFactory()
    factories.TopicCuratorFactory(user=user, topic=topic)
    factories.create_topic_posts(topic, user, [
        ('event', 0, 1, 'Balsavimo internetu koncepcijos patvirtinimas', 'lrs.lt', '2006-11-26'),
        ('quote', 'Mantas Adomėnas', 'seimo narys', 'kauno.diena.lt', '2016-03-22', [
            (1, 0, 'Nepasiduokime paviršutiniškiems šūkiams – šiuolaikiška, modernu.', [
                (1, 'šiuolaikiška, modernu', True),
            ]),
            (1, 0, 'Atidaroma galimybė prekiauti balsais ir likti nebaudžiamam.', [
                (-1, 'balsų pirkimas', None),
            ]),
        ]),
        ('quote', 'Eligijus Masiulis', 'seimo narys', 'delfi.lt', '2015-10-08', [
            (0, 0, 'Mes palaikysim tokį įstatymą, nes turime žengti į priekį ir reaguoti į XXI a. iššūkius.', [
                (1, 'šiuolaikiška, modernu', None),
            ]),
        ]),
    ])
    group = factories.GroupFactory(members=models.Actor.objects.all())
    app.get(reverse('compare-positions', args=[group.pk, group.slug]), user=user)
