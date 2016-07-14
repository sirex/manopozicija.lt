import itertools

from manopozicija import services
from manopozicija import factories


def test_get_topic_arguments(app):
    arguments = [
        (+1, False, 'didesnis užsienio lietuvių aktyvumas rinkimuose'),
        (+1, True, 'šiuolaikiška, modernu'),
        (+1, False, 'šiuolaikiška, modernu'),
        (-1, False, 'balsavimas nekontroliuojamoje aplinkoje'),
        (-1, True, 'balsų pirkimas'),
        (-1, False, 'balsų pirkimas'),
        (-1, False, 'balsų pirkimas'),
    ]
    topic = factories.TopicFactory()
    for position, counterargument, argument in arguments:
        factories.ArgumentFactory(topic=topic, position=position, title=argument, counterargument=counterargument)
    assert list(services.get_topic_arguments(topic).values_list('count', 'position', 'title')) == [
        (1, +1, 'didesnis užsienio lietuvių aktyvumas rinkimuose'),
        (1, +1, 'šiuolaikiška, modernu'),
        (2, -1, 'balsų pirkimas'),
        (1, -1, 'balsavimas nekontroliuojamoje aplinkoje'),
    ]


def test_get_topic_posts(app):
    topic = factories.TopicFactory()
    factories.create_topic_posts(topic, [
        ('event', 1, 0, 'Balsavimo internetu koncepcijos patvirtinimas', 'lrs.lt', '2006-11-26'),
        ('quote', 'Mantas Adomėnas', 'seimo narys', 'kauno.diena.lt', '2016-03-22', [
            (4, 0, 'Nepasiduokime paviršutiniškiems šūkiams – šiuolaikiška, modernu.', [
                (1, 'šiuolaikiška, modernu', True),
            ]),
            (0, 0, 'Atidaroma galimybė prekiauti balsais ir likti nebaudžiamam.', [
                (-1, 'balsų pirkimas', None),
            ]),
        ]),
    ])
    assert services.dump_topic_posts(topic) == '\n'.join([
        '( ) (n) Mantas Adomėnas (seimo narys)                                          kauno.diena.lt 2016-03-22    ',
        ' |      Nepasiduokime paviršutiniškiems šūkiams – šiuolaikiška, modernu.                                 (4)',
        ' |      - (y) šiuolaikiška, modernu < (counterargument)                                                     ',
        ' |      Atidaroma galimybė prekiauti balsais ir likti nebaudžiamam.                                      (0)',
        ' |      - (n) balsų pirkimas                                                                                ',
        ' |                                                                                                          ',
        ' o  (-) Balsavimo internetu koncepcijos patvirtinimas                                  lrs.lt 2006-11-26 (1)',
    ])


def test_create_quote(app):
    user = factories.UserFactory()
    topic = factories.TopicFactory()

    # First try to create a quote as no non-curator user
    source, quote, arguments = factories.get_quote_form_data(
        text='Nepasiduokime paviršutiniškiems šūkiams – šiuolaikiška, modernu.'
    )
    services.create_quote(user, topic, source, quote, arguments)
    assert services.dump_topic_posts(topic) == ''
    assert services.dump_topic_posts(topic, queue=True) == '\n'.join([
        '( ) (n) Mantas Adomėnas (seimo narys)                                          kauno.diena.lt 2016-03-22    ',
        ' |      Nepasiduokime paviršutiniškiems šūkiams – šiuolaikiška, modernu.                                 (0)',
        ' |      - (y) šiuolaikiška, modernu < (counterargument)                                                     ',
    ])

    # Now create a post as a curator user
    factories.TopicCuratorFactory(user=user, topic=topic)
    source, quote, arguments = factories.get_quote_form_data(
        text='Atidaroma galimybė prekiauti balsais ir likti nebaudžiamam.'
    )
    services.create_quote(user, topic, source, quote, arguments)
    assert services.dump_topic_posts(topic) == '\n'.join([
        '( ) (n) Mantas Adomėnas (seimo narys)                                          kauno.diena.lt 2016-03-22    ',
        ' |      Atidaroma galimybė prekiauti balsais ir likti nebaudžiamam.                                      (0)',
        ' |      - (y) šiuolaikiška, modernu < (counterargument)                                                     ',
    ])


def test_get_post_votes(app):
    user = (factories.UserFactory(first_name='u%d' % i) for i in itertools.count())
    event = factories.EventFactory()
    post = factories.PostFactory(content_object=event)
    assert services.get_post_votes(post) == (0, 0)
    assert services.update_user_position(next(user), post, 1) == (1, 0)
    assert services.update_user_position(next(user), post, 1) == (2, 0)
    assert services.update_user_position(next(user), post, -1) == (2, 1)
    assert services.get_post_votes(post) == (2, 1)

    # Try to vote several times with the same user
    user = factories.UserFactory()
    assert services.update_user_position(user, post, 1) == (3, 1)
    assert services.update_user_position(user, post, -1) == (2, 2)
    assert services.update_user_position(user, post, -1) == (2, 2)
    assert services.update_user_position(user, post, 1) == (3, 1)
    assert services.get_post_votes(post) == (3, 1)
