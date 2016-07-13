def _get_position_image(position, positive, negative, neutral):
    if position > 0.5:
        return positive
    elif position < -0.5:
        return negative
    else:
        return neutral


def get_posts(posts):
    result = []
    for post in posts:
        if post['type'] == 'event':
            event = post['event']
            result.append({
                'type': 'event',
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
                    'upvotes': post['post'].upvotes,
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
                    'upvotes': post.upvotes,
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
                    } for argument in quote.argument_set.all()],
                } for post, quote in post['quotes']],
            })
    return result
