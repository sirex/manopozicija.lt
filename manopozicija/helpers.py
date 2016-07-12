def _get_source_position_image(position):
    if position > 0.5:
        return 'img/actor-positive.png'
    elif position < 0.5:
        return 'img/actor-negative.png'
    else:
        return 'img/actor-neutral.png'


def get_posts(posts):
    result = []
    for post in posts:
        if post['type'] == 'event':
            result.append(post)
        else:
            source = post['source']
            actor = source.actor
            result.append({
                'source': {
                    'link': source.source_link,
                    'title': source.source_title,
                    'actor': {
                        'name': str(actor),
                        'title': source.actor_title or actor.title,
                        'photo': actor.photo,
                        'position_image': _get_source_position_image(source.position),
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
