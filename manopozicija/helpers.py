import itertools

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
    user_votes = services.get_user_topic_votes(user, topic)
    curator_votes = services.get_curator_topic_votes(user, topic)
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
                    } for argument in quote.argument_set.order_by('pk')],
                } for post, quote in post['quotes']],
            })
    return result


def get_arguments(arguments):
    groups = itertools.groupby(arguments, key=lambda x: x['position'])
    positive = list(next(groups, (+1, []))[1])
    negative = list(next(groups, (-1, []))[1])
    return list(itertools.zip_longest(positive, negative))
