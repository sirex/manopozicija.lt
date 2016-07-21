import itertools

from manopozicija import models
from manopozicija import services
from manopozicija import factories


def test_get_topic_arguments(app):
    topic = factories.TopicFactory()
    factories.create_arguments(topic, [
        (+1, False, 'didesnis užsienio lietuvių aktyvumas rinkimuose'),
        (+1, True, 'šiuolaikiška, modernu'),
        (+1, False, 'šiuolaikiška, modernu'),
        (-1, False, 'balsavimas nekontroliuojamoje aplinkoje'),
        (-1, True, 'balsų pirkimas'),
        (-1, False, 'balsų pirkimas'),
        (-1, False, 'balsų pirkimas'),
    ])
    assert list(services.get_topic_arguments(topic).values_list('count', 'position', 'title')) == [
        (1, +1, 'didesnis užsienio lietuvių aktyvumas rinkimuose'),
        (1, +1, 'šiuolaikiška, modernu'),
        (2, -1, 'balsų pirkimas'),
        (1, -1, 'balsavimas nekontroliuojamoje aplinkoje'),
    ]


def test_get_topic_posts(app):
    user = factories.UserFactory()
    topic = factories.TopicFactory()
    factories.TopicCuratorFactory(user=user, topic=topic)
    factories.create_topic_posts(topic, None, [
        ('event', 1, 0, 'Balsavimo internetu koncepcijos patvirtinimas', 'lrs.lt', '2006-11-26'),
        ('quote', 'Mantas Adomėnas', 'seimo narys', 'kauno.diena.lt', '2016-03-22', [
            (1, 0, 'Nepasiduokime paviršutiniškiems šūkiams – šiuolaikiška, modernu.', [
                (1, 'šiuolaikiška, modernu', True),
            ]),
            (0, 0, 'Atidaroma galimybė prekiauti balsais ir likti nebaudžiamam.', [
                (-1, 'balsų pirkimas', None),
            ]),
        ]),
    ])
    assert services.dump_topic_posts(topic) == '\n'.join([
        '( ) (n) Mantas Adomėnas (seimo narys)                                          kauno.diena.lt 2016-03-22    ',
        ' |      Nepasiduokime paviršutiniškiems šūkiams – šiuolaikiška, modernu.                                 (1)',
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
        '( ) (-) Mantas Adomėnas (seimo narys)                                          kauno.diena.lt 2016-03-22    ',
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

    assert services.get_user_topic_votes(user, post.topic) == {post.pk: 1}


def test_curator_votes(app):
    users = (factories.UserFactory(first_name='u%d' % i) for i in itertools.count())
    event = factories.EventFactory()
    post = factories.PostFactory(content_object=event)
    assert services.get_curator_votes(post) == (0, 0)
    assert services.update_curator_position(next(users), post, 1) == (1, 0)
    assert services.update_curator_position(next(users), post, 1) == (2, 0)
    assert services.update_curator_position(next(users), post, -1) == (2, 1)
    assert services.get_curator_votes(post) == (2, 1)

    # Try to vote several times with the same user
    user = factories.UserFactory()
    assert services.update_curator_position(user, post, 1) == (3, 1)
    assert services.update_curator_position(user, post, -1) == (2, 2)
    assert services.update_curator_position(user, post, -1) == (2, 2)
    assert services.update_curator_position(user, post, 1) == (3, 1)
    assert services.get_curator_votes(post) == (3, 1)

    assert services.get_curator_topic_votes(user, post.topic) == {post.pk: 1}

    # Try to vote for new curator application
    curator = factories.CuratorFactory(user=user)
    post = factories.PostFactory(content_object=curator)
    user_1, user_2, user_3 = next(users), next(users), next(users)

    # Initially user should not be a curator
    assert services.is_topic_curator(user, post.topic) is False

    # After first positive vote user shuould become a curator
    assert services.update_curator_position(user_1, post, 1) == (1, 0)
    assert services.is_topic_curator(user, post.topic) is True

    # When number of curator upvotes and downvotes becomes equal, user should be removed from curators
    assert services.update_curator_position(user_1, post, -1) == (0, 1)
    assert services.is_topic_curator(user, post.topic) is False

    # Same thing, but with two users voting differently
    assert services.update_curator_position(user_2, post, 1) == (1, 1)
    assert services.is_topic_curator(user, post.topic) is False

    # If third users agrees to accept new curator it will be accepted
    assert services.update_curator_position(user_3, post, 1) == (2, 1)
    assert services.is_topic_curator(user, post.topic) is True


def test_compare_positions(app):
    user = factories.UserFactory()
    topic = factories.TopicFactory()
    factories.TopicCuratorFactory(user=user, topic=topic)

    # Fill topic with some content
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
        ('quote', 'Juozas Bernatonis', 'seimo narys', 'delfi.lt', '2016-03-26', [
            (0, 1, 'Žemas užsienio lietuvių aktyvumas susijęs su dalyvavimo rinkimuose sunkumais.', [
                (1, 'didės užsienio lietuvių aktyvumas rinkimuose', None),
            ]),
        ]),
    ])

    # Check topic was actually filled with correct data
    assert services.dump_topic_posts(topic) == '\n'.join([
        '( ) (y) Juozas Bernatonis (seimo narys)                                              delfi.lt 2016-03-26    ',
        ' |      Žemas užsienio lietuvių aktyvumas susijęs su dalyvavimo rinkimuose sunkumais.                   (-1)',
        ' |      - (y) didės užsienio lietuvių aktyvumas rinkimuose                                                  ',
        ' |                                                                                                          ',
        '( ) (n) Mantas Adomėnas (seimo narys)                                          kauno.diena.lt 2016-03-22    ',
        ' |      Nepasiduokime paviršutiniškiems šūkiams – šiuolaikiška, modernu.                                 (1)',
        ' |      - (y) šiuolaikiška, modernu < (counterargument)                                                     ',
        ' |      Atidaroma galimybė prekiauti balsais ir likti nebaudžiamam.                                      (1)',
        ' |      - (n) balsų pirkimas                                                                                ',
        ' |                                                                                                          ',
        '( ) (y) Eligijus Masiulis (seimo narys)                                              delfi.lt 2015-10-08    ',
        ' |      Mes palaikysim tokį įstatymą, nes turime žengti į priekį ir reaguoti į XXI a. iššūkius.          (0)',
        ' |      - (y) šiuolaikiška, modernu                                                                         ',
        ' |                                                                                                          ',
        ' o  (-) Balsavimo internetu koncepcijos patvirtinimas                                  lrs.lt 2006-11-26 (-1)',
    ])

    mantas_adomenas = models.Actor.objects.get(first_name='Mantas', last_name='Adomėnas').pk
    eligijus_masiulis = models.Actor.objects.get(first_name='Eligijus', last_name='Masiulis').pk

    group = factories.GroupFactory(members=[mantas_adomenas, eligijus_masiulis])

    # Check list of actor and user positions for quotes
    assert list(services.get_user_quote_positions(group, user)) == [
        (mantas_adomenas, -1.0, 1),
        (mantas_adomenas, -1.0, 1),
        (eligijus_masiulis, 1.0, 0),
    ]

    # Check list of actor and user positions for arguments
    assert list(services.get_user_argument_positions(group, user)) == [
        ('balsų pirkimas', mantas_adomenas, -1.0, -1.0),
        ('šiuolaikiška, modernu', mantas_adomenas, -1.0, -1.0),
        ('šiuolaikiška, modernu', eligijus_masiulis, 1.0, -1.0),
    ]

    # Check list of actor and user positions for events
    assert list(services.get_user_event_positions(group, user)) == [
    ]

    # Finally check if position comparison works
    assert services.compare_positions(group, user) == [
        (mantas_adomenas, 0.0),
        (eligijus_masiulis, 1.0),
    ]
