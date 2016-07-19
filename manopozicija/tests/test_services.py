import itertools

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
    topic = factories.TopicFactory()
    factories.create_topic_posts(topic, None, [
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
    assert services.dump_actor_positions(topic) == '\n'.join([
        '- Atidaroma galimybė prekiauti balsais ir likti nebaudžiamam.',
        '  -1.0 Mantas Adomėnas (aktorius)',
    ])


def test_actor_positions(app):
    user = factories.UserFactory()
    topic = factories.TopicFactory()
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
            (0, 1, 'Mes palaikysim tokį įstatymą, nes turime žengti į priekį ir reaguoti į XXI a. iššūkius.', [
                (1, 'šiuolaikiška, modernu', None),
            ]),
        ]),
    ])
    assert services.dump_topic_posts(topic) == '\n'.join([
        '( ) (n) Mantas Adomėnas (seimo narys)                                          kauno.diena.lt 2016-03-22    ',
        ' |      Nepasiduokime paviršutiniškiems šūkiams – šiuolaikiška, modernu.                                 (1)',
        ' |      - (y) šiuolaikiška, modernu < (counterargument)                                                     ',
        ' |      Atidaroma galimybė prekiauti balsais ir likti nebaudžiamam.                                      (1)',
        ' |      - (n) balsų pirkimas                                                                                ',
        ' |                                                                                                          ',
        '( ) (y) Eligijus Masiulis (seimo narys)                                              delfi.lt 2015-10-08    ',
        ' |      Mes palaikysim tokį įstatymą, nes turime žengti į priekį ir reaguoti į XXI a. iššūkius.         (-1)',
        ' |      - (y) šiuolaikiška, modernu                                                                         ',
        ' |                                                                                                          ',
        ' o  (-) Balsavimo internetu koncepcijos patvirtinimas                                  lrs.lt 2006-11-26 (-1)',
    ])

    from django.db.models import FloatField
    from django.db.models import F, Case, When, Sum, ExpressionWrapper
    from manopozicija.db import Sqrt, Power
    from manopozicija import models

    weight = Case(
        When(post__actorposition__origin=models.ActorPosition.ACTOR, then=3),
        When(post__actorposition__origin=models.ActorPosition.ARGUMENT, then=2),
        When(post__actorposition__origin=models.ActorPosition.VOTING, then=1),
        default=1,
        output_field=FloatField(),
    )
    qs = (
        models.UserPostPosition.objects.
        filter(user=user).
        annotate(actor=F('post__actorposition__actor')).
        values('user', 'actor').
        annotate(
            # distance(user, actor) == sum(origin * sqrt((user.position - actor.position)**2) / 2) / sum(origin)
            distance=ExpressionWrapper((
                Sum(weight * Sqrt(Power(F('position') - F('post__actorposition__position'), 2)) / 2) / Sum(weight)
            ), output_field=FloatField()),
        )
    )


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
    actors = [factories.PersonActorFactory(first_name='U%d' % i) for i in range(3)]
    factories.create_actor_positions([
        (user, +1, [(actors[0], 'ACTOR', +1),
                    (actors[1], 'ARGUMENT', -1),
                    (actors[2], 'ARGUMENT', +1)]),
        (user, -1, [(actors[0], 'ARGUMENT', +1),
                    (actors[1], 'ACTOR', +1),
                    (actors[2], 'ARGUMENT', +1)]),
    ])
    # distance(user, actor) == sum(origin * sqrt((user_position - actor_position)**2) / 2) / sum(origin)
    # distance(user, actors[0]) == sum(
    #       3 * sqrt(( 1 - 1)**2) / 2,
    #       2 * sqrt((-1 - 1)**2) / 2,
    #   ) / sum(3, 2) == 0.4
    assert list(services.compare_positions(user).order_by('post__actorposition__actor_id')) == [
        {'user': user.pk, 'actor': actors[0].pk, 'distance': 0.4},
        {'user': user.pk, 'actor': actors[1].pk, 'distance': 1.0},
        {'user': user.pk, 'actor': actors[2].pk, 'distance': 0.5},
    ]
