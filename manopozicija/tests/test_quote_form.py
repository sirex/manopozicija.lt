from django.core.urlresolvers import reverse

from manopozicija import models
from manopozicija import services
from manopozicija import factories


def test_update_with_same_quote(app):
    # This snippet allows to run tests without running slow migrations
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')

    user = factories.UserFactory()
    topic = factories.TopicFactory()
    factories.TopicCuratorFactory(user=user, topic=topic)
    post, = factories.create_topic_posts(topic, user, [
        ('quote', 'Mantas Adomėnas', 'seimo narys', 'kauno.diena.lt', '2016-03-22', [
            (1, 0, 'Nepasiduokime paviršutiniškiems šūkiams.', [
                # position, argument, counterargument
                (1, 'šiuolaikiška, modernu', None),
            ]),
        ]),
    ])

    resp = app.get(reverse('quote-update', args=[post.pk]), user='vardenis')
    form = resp.forms['quote-form']
    form['timestamp'] = '2016-04-04 16:34'
    resp = form.submit()

    assert resp.status == '302 Found'
    assert resp.headers['location'] == topic.get_absolute_url()
    assert services.dump_topic_posts(topic) == '\n'.join([
        '( ) (y) Mantas Adomėnas (seimo narys)                                          kauno.diena.lt 2016-04-04    ',
        ' |      Nepasiduokime paviršutiniškiems šūkiams.                                                         (0)',
        ' |      - (y) šiuolaikiška, modernu                                                                         ',
    ])
