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


def test_create_event(app):
    factories.UserFactory()
    topic = factories.TopicFactory()

    resp = app.get(reverse('event-create', args=[topic.pk, topic.slug]), user='vardenis')
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
    resp = app.get(reverse('event-create', args=[topic.pk, topic.slug]), user='vardenis')
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
    factories.UserFactory()
    actor = factories.PersonActorFactory()
    topic = factories.TopicFactory()

    resp = app.get(reverse('quote-create', args=[topic.pk, topic.slug]), user='vardenis')
    form = resp.forms['quote-form']
    form['actor'] = actor.pk
    form['source_link'] = 'http://kauno.diena.lt/naujienos/lietuva/politika/skinasi-kelia-balsavimas-internetu-740017'
    form['timestamp'] = '2016-03-22 16:34'
    form['text'] = 'Nepasiduokime paviršutiniškiems šūkiams – šiuolaikiška, modernu.'
    form['form-0-title'] = 'šiuolaikiška, modernu'
    form['form-0-counterargument'] = True
    resp = form.submit()

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

    assert resp.headers['location'] == topic.get_absolute_url()
    assert services.dump_topic_posts(topic) == '\n'.join([
        '( ) (n) Mantas Adomėnas (seimo narys)                                          kauno.diena.lt 2016-03-22    ',
        ' |      Nepasiduokime paviršutiniškiems šūkiams – šiuolaikiška, modernu.                                 (0)',
        ' |      - (y) šiuolaikiška, modernu < (counterargument)                                                     ',
        ' |      Atidaroma galimybė prekiauti balsais ir likti nebaudžiamam.                                      (0)',
        ' |      - (n) balsų pirkimas                                                                                ',
    ])
