import itertools

from django.db.models import Q, Max

from manopozicija import models
from manopozicija import services


def _get_position_image(position, positive, negative, neutral):
    if position > 0.5:
        return positive
    elif position < -0.5:
        return negative
    else:
        return neutral


def _get_post_context(post, user_votes, curator_votes):
    votes = user_votes if post.approved else curator_votes
    return {
        'id': post.pk,
        'votes': services.get_post_votes_display(post),
        'user': {
            'upvote': 'active' if votes.get(post.pk, 0) > 0 else '',
            'downvote': 'active' if votes.get(post.pk, 0) < 0 else '',
        },
        'save_vote': 'manopozicija.save_user_vote' if post.approved else 'manopozicija.save_curator_vote',
    }


def get_posts(user, topic, posts):
    result = []
    user_votes = services.get_user_topic_votes(user, topic) if user.is_authenticated() else {}
    curator_votes = services.get_curator_topic_votes(user, topic) if user.is_authenticated() else {}
    for post in posts:
        if post['type'] == 'event':
            event = post['event']
            result.append({
                'type': 'event',
                'post': _get_post_context(post['post'], user_votes, curator_votes),
                'event': {
                    'position_image': _get_position_image(
                        event.position,
                        'img/event-positive.png',
                        'img/event-negative.png',
                        'img/event-neutral.png',
                    ),
                    'name': event.title,
                    'timestamp': event.timestamp.strftime('%Y-%m-%d'),
                    'source': {
                        'link': event.source_link,
                        'name': event.source_title,
                    },
                },
            })
        elif post['type'] == 'curator':
            curator = post['curator']
            position = services.get_user_topic_position(curator.user, topic)
            result.append({
                'type': 'curator',
                'post': _get_post_context(post['post'], user_votes, curator_votes),
                'curator': {
                    'position_image': _get_position_image(
                        position,
                        'img/actor-positive.png',
                        'img/actor-negative.png',
                        'img/actor-neutral.png',
                    ),
                    'name': str(curator.user),
                    'title': curator.title,
                    'photo': curator.photo,
                },
            })
        else:
            source = post['source']
            actor = source.actor
            result.append({
                'type': 'quotes',
                'source': {
                    'link': source.source_link,
                    'name': source.source_title,
                    'actor': {
                        'name': str(actor),
                        'title': source.actor_title or actor.title,
                        'photo': actor.photo,
                        'position_image': _get_position_image(
                            source.position,
                            'img/actor-positive.png',
                            'img/actor-negative.png',
                            'img/actor-neutral.png',
                        ),
                    },
                },
                'quotes': [{
                    'text': quote.text,
                    'post': _get_post_context(post, user_votes, curator_votes),
                    'vote': {
                        'img': {
                            'top': 'img/thumb-up.png',
                            'bottom': 'img/thumb-down.png',
                        },
                    },
                    'arguments': [{
                        'name': argument.title,
                        'classes': 'text-%s' % ('danger' if argument.position < 0 else 'success'),
                        'counterargument': {
                            'classes': 'glyphicon glyphicon-%s' % ('remove' if argument.counterargument else 'tag'),
                        }
                    } for argument in quote.postargument_set.order_by('pk')],
                } for post, quote in post['quotes']],
            })
    return result


def get_arguments(arguments):
    positive = []
    negative = []
    for key, group in itertools.groupby(arguments, key=lambda x: x['position']):
        if key > 0:
            positive = list(group)
        else:
            negative = list(group)
    return list(itertools.zip_longest(positive, negative))


def _actor_details(groups, actors, actor_id, distance):
    if actor_id:
        return {
            'actor': actors[actor_id],
            'group': groups.get(actor_id),
            'distance': distance,
        }
    else:
        return None


def get_positions(group, user, limit=20):
    threshold = 0.4
    actors = {x.pk: x for x in group.members.all()}
    groups = {
        x.actor_id: x.group for x in (
            models.Member.objects.filter(
                Q(until__lte=group.timestamp) | Q(until__isnull=True),
                since__gte=group.timestamp,
                actor__ingroup=group,
                group__title='politinė partija',
            ).
            select_related('group').
            order_by('-since')
        )
    }
    positions = services.compare_positions(group, user)
    compat = ((x, d) for x, d in positions if d < threshold)
    incompat = ((x, d) for x, d in reversed(positions) if d >= threshold)
    result = []
    for i, (left, right) in zip(range(limit), itertools.zip_longest(compat, incompat, fillvalue=(None, None))):
        result.append((
            _actor_details(groups, actors, *left),
            _actor_details(groups, actors, *right),
        ))
    return result


def get_topic_curators(topic):
    result = []
    for curator in services.get_topic_curators(topic):
        position = services.get_user_topic_position(curator.user, topic)
        result.append({
            'obj': curator,
            'name': curator.user.get_full_name(),
            'photo': curator.photo,
            'title': curator.title,
            'position_image': _get_position_image(
                position,
                'img/actor-positive.png',
                'img/actor-negative.png',
                'img/actor-neutral.png',
            ),
        })
    return result


def get_topics():
    result = []
    topics = (
        models.Topic.objects.
        order_by('pk').
        annotate(updated=Max('post__timestamp')).
        order_by('-updated')
    )
    for topic in topics:
        result.append({
            'obj': topic,
            'is_svg': topic.logo.name.endswith('.svg'),
        })
    return result


def get_indicators(topic):
    return [
        {
            'id': x.pk,
            'title': x.title,
            'source_link': x.source,
            'source_title': services.get_title_from_link(x.source),
            'last_update': x.last_update,
        }
        for x in topic.indicators.all()
    ]
