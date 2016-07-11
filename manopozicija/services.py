import itertools

from django.db.models import Count

import manopozicija.models as mp


def get_topic_arguments(topic):
    return (
        mp.Argument.objects.
        values('position', 'title').
        filter(topic=topic, counterargument=False).
        annotate(count=Count('title')).
        order_by('-count')
    )


def get_topic_posts(topic):
    result = []
    qs = (
        mp.Post.objects.
        filter(topic=topic).
        order_by('-timestamp')
    )
    groups = itertools.groupby(qs, key=lambda x: (x.content_type.app_label, x.content_type.model))
    for content_type, posts in groups:
        if content_type == ('manopozicija', 'event'):
            for post in posts:
                result.append({
                    'type': post.content_type.model,
                    'post': post,
                    'event': post.content_object,
                })
        elif content_type == ('manopozicija', 'quote'):
            for _, quotes in itertools.groupby(posts, key=lambda x: x.content_object.source.pk):
                quotes = list(quotes)
                result.append({
                    'type': quotes[0].content_type.model,
                    'source': quotes[0].content_object.source,
                    'quotes': [(x, x.content_object) for x in quotes],
                })
        else:
            raise ValueError('Unknown content type: %r' % content_type)
    return result


def _format_position(position):
    if position > 0.5:
        return '(y)'
    elif position < -0.5:
        return '(n)'
    else:
        return '(-)'


def _align_both_sides(left, rigth, width):
    return left + rigth.rjust(width - len(left))


def dump_topic_posts(topic):
    width = 108
    middle = width - 12
    result = []
    for i, row in enumerate(get_topic_posts(topic)):
        if i > 0:
            result.append(' | ' + ' ' * (width - 3))
        if row['type'] == 'event':
            result.append(' o  {position} {middle} ({upvotes})'.format(
                position=_format_position(row['event'].position),
                middle=_align_both_sides(
                    row['event'].title,
                    '%s %s' % (row['event'].source_title, row['post'].timestamp.strftime('%Y-%m-%d')),
                    middle,
                ),
                upvotes=row['post'].upvotes,
            ))
        else:
            result.append('( ) {position} {middle}    '.format(
                position=_format_position(row['source'].position),
                middle=_align_both_sides(
                    '%s (%s)' % (
                        ' '.join([row['source'].actor.first_name, row['source'].actor.last_name]),
                        row['source'].actor_title,
                    ),
                    '%s %s' % (
                        row['source'].source_title,
                        row['source'].timestamp.strftime('%Y-%m-%d'),
                    ),
                    middle,
                ),
            ))
            for post, quote in row['quotes']:
                result.append(' |      %s' % _align_both_sides(quote.text, '(%s)' % post.upvotes, middle + 4))
                for argument in quote.argument_set.all():
                    if argument.counterargument and argument.counterargument_title:
                        counterargument = ' < ' + argument.counterargument_title
                    elif argument.counterargument:
                        counterargument = ' < (counterargument)'
                    else:
                        counterargument = ''
                    result.append(_align_both_sides(' |      - {position} {argument}{counterargument}'.format(
                        position=_format_position(argument.position),
                        argument=argument.title,
                        counterargument=counterargument,
                    ), '', width))
    return '\n'.join(result)
