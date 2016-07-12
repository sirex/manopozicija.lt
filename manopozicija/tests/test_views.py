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


def test_create_quote(app):
    factories.UserFactory()
    actor = factories.PersonActorFactory()
    topic = factories.TopicFactory()

    resp = app.get(reverse('quote-create', args=[topic.pk, topic.slug]), user='vardenis')
    form = resp.forms['quote-form']
    form['actor'] = actor.pk
    form['actor_title'] = 'seimo narys'
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
    form['actor_title'] = 'seimo narys'
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
