import urllib
import itertools

from django.utils import timezone
from django.db.models import FloatField
from django.db.models import F, Case, When, Count, Sum, Avg, ExpressionWrapper
from django.utils.translation import ugettext
from django.contrib.contenttypes.models import ContentType

from manopozicija.db import Sqrt, Power
from manopozicija import models


def create_event(user, topic, event: dict):
    source_link = event.pop('source_link')
    event['user'] = user
    event['type'] = models.Event.DOCUMENT
    event['position'] = 0
    event['source_title'] = get_title_from_link(source_link)
    event, created = models.Event.objects.get_or_create(source_link=source_link, defaults=event)

    is_curator = is_topic_curator(user, topic)
    approved = timezone.now() if is_curator else None

    post = models.Post.objects.create(
        body=topic.default_body,
        topic=topic,
        position=0,
        approved=approved,
        timestamp=event.timestamp,
        upvotes=0,
        content_object=event,
    )

    if is_curator:
        # Automatically approve posts created by topic curators.
        models.PostLog.objects.create(user=user, post=post, action=models.PostLog.VOTE, vote=1)

    return event


def create_quote(user, topic, source: dict, quote: dict, arguments: list):
    source['actor_title'] = source['actor'].title
    source['source_title'] = get_title_from_link(source['source_link'])
    source, created = models.Source.objects.get_or_create(
        actor=source['actor'],
        source_link=source['source_link'],
        defaults=source,
    )

    quote = models.Quote.objects.create(user=user, source=source, **quote)

    is_curator = is_topic_curator(user, topic)
    approved = timezone.now() if is_curator else None

    post = models.Post.objects.create(
        body=topic.default_body,
        topic=topic,
        actor=source.actor,
        position=0,
        approved=approved,
        timestamp=source.timestamp,
        upvotes=0,
        content_object=quote,
    )

    if is_curator:
        # Automatically approve posts created by topic curators.
        models.PostLog.objects.create(user=user, post=post, action=models.PostLog.VOTE, vote=1)

    for argument in arguments:
        if argument.get('title'):
            models.PostArgument.objects.create(topic=topic, post=post, quote=quote, **argument)
            argument_, created = models.Argument.objects.get_or_create(topic=topic, title=argument['title'])
            position = argument['position'] * (-1 if argument['counterargument'] else 1)
            models.ActorArgumentPosition.objects.update_or_create(actor=source.actor, argument=argument_, defaults={
                'position': position,
            })

    post.position = get_quote_position(topic, quote)
    post.save()

    source.position = get_source_position(topic, source)
    source.save()

    return quote


def create_curator(user, topic, user_data: dict, curator: dict):
    curator, created = models.Curator.objects.get_or_create(user=user, defaults=curator)
    if user_data:
        user.first_name = user_data['first_name']
        user.last_name = user_data['last_name']
        user.save()

    # Add new curator as a topic post to be approved by other curators.
    models.Post.objects.create(
        body=topic.default_body,
        topic=topic,
        actor=None,
        position=0,
        approved=None,
        timestamp=timezone.now(),
        upvotes=0,
        content_object=curator,
    )

    return curator


def is_topic_curator(user, topic):
    return models.TopicCurator.objects.filter(user=user, topic=topic, approved__isnull=False).exists()


def get_title_from_link(link):
    title = urllib.parse.urlparse(link).netloc
    if title.startswith('www.'):
        title = title[4:]
    return title


def get_source_position(topic, source):
    agg = (
        models.PostArgument.objects.
        filter(topic=topic, quote__source=source, post__approved__isnull=False).
        aggregate(position=Avg(Case(
            When(counterargument=True, then=F('position') * -1),
            default=F('position')
        )))
    )
    return agg['position'] or 0


def get_quote_position(topic, quote):
    agg = (
        models.PostArgument.objects.
        filter(topic=topic, quote=quote, post__approved__isnull=False).
        aggregate(position=Avg(Case(
            When(counterargument=True, then=F('position') * -1),
            default=F('position')
        )))
    )
    return agg['position'] or 0


def get_topic_arguments(topic):
    return (
        models.PostArgument.objects.
        values('position', 'title').
        filter(topic=topic, counterargument=False, post__approved__isnull=False).
        annotate(count=Count('title')).
        order_by('-position', '-count', 'title')
    )


def get_topic_posts(topic, queue=False):
    result = []

    if queue:
        qs = (
            models.Post.objects.
            filter(topic=topic, approved__isnull=True).
            order_by('-created', '-pk')
        )
    else:
        curator_type = ContentType.objects.get(app_label='manopozicija', model='curator')
        qs = (
            models.Post.objects.
            exclude(content_type=curator_type).
            filter(topic=topic, approved__isnull=False).
            order_by('-timestamp', 'pk')
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
        elif content_type == ('manopozicija', 'curator'):
            for post in posts:
                result.append({
                    'type': post.content_type.model,
                    'post': post,
                    'curator': post.content_object,
                })
        else:
            raise ValueError('Unknown content type: %r' % (content_type,))
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


def get_post_votes_display(post):
    if post.approved:
        upvotes = post.upvotes
        downvotes = post.downvotes
        return upvotes if upvotes >= downvotes else -downvotes
    else:
        upvotes = post.curator_upvotes
        downvotes = post.curator_downvotes
        return upvotes if upvotes > downvotes else -downvotes


def dump_topic_posts(topic, **kwargs):
    width = 108
    middle = width - 12
    result = []
    for i, row in enumerate(get_topic_posts(topic, **kwargs)):
        if i > 0:
            result.append(' | ' + ' ' * (width - 3))
        if row['type'] == 'event':
            result.append(' o  {position} {middle} ({votes})'.format(
                position=_format_position(row['event'].position),
                middle=_align_both_sides(
                    row['event'].title,
                    '%s %s' % (row['event'].source_title, row['post'].timestamp.strftime('%Y-%m-%d')),
                    middle,
                ),
                votes=get_post_votes_display(row['post']),
            ))
        elif row['type'] == 'curator':
            result.append('( ) {middle} ({votes})'.format(
                middle=_align_both_sides(
                    '%s (%s)' % (
                        row['curator'].user.get_full_name(),
                        row['curator'].title,
                    ),
                    ugettext("naujas temos kuratorius"),
                    middle,
                ),
                votes=get_post_votes_display(row['post']),
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
                votes = get_post_votes_display(post)
                result.append(' |      %s' % _align_both_sides(quote.text, '(%s)' % votes, middle + 4))
                for argument in quote.postargument_set.order_by('title'):
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


def get_post_votes(post):
    agg = models.UserPostPosition.objects.filter(post=post).aggregate(
        upvotes=Sum(Case(When(position__gt=0, then=F('position')), default=0)),
        downvotes=Sum(Case(When(position__lt=0, then=F('position')), default=0)),
    )
    return agg['upvotes'] or 0, abs(agg['downvotes'] or 0)


def update_user_post_argument_positions(user, post):
    post_arguments = list(post.postargument_set.distinct().values_list('title', flat=True))
    rows = (
        models.UserPostPosition.objects.
        filter(post__topic=post.topic).
        exclude(position=0).
        annotate(argument=F('post__postargument__title')).
        values('argument').
        annotate(position=Avg(Case(
            When(post__postargument__counterargument=True, then=F('post__postargument__position') * -1),
            default=F('post__postargument__position'),
        ) * F('position'))).
        filter(argument__in=post_arguments)
    )
    for row in rows:
        argument, created = models.Argument.objects.get_or_create(topic=post.topic, title=row['argument'])
        models.UserArgumentPosition.objects.update_or_create(user=user, argument=argument, defaults={
            'position': row['position'],
        })


def update_user_position(user, post, vote: int):
    models.UserPostPosition.objects.update_or_create(user=user, post=post, defaults={'position': vote})
    post.upvotes, post.downvotes = get_post_votes(post)
    post.save()
    update_user_post_argument_positions(user, post)
    return post.upvotes, post.downvotes


def get_curator_votes(post):
    agg = models.PostLog.objects.filter(post=post).aggregate(
        upvotes=Sum(Case(When(vote__gt=0, then=F('vote')), default=0)),
        downvotes=Sum(Case(When(vote__lt=0, then=F('vote')), default=0)),
    )
    return agg['upvotes'] or 0, abs(agg['downvotes'] or 0)


def update_curator_position(user, post, vote: int):
    models.PostLog.objects.update_or_create(user=user, post=post, action=models.PostLog.VOTE, defaults={'vote': vote})

    post.curator_upvotes, post.curator_downvotes = get_curator_votes(post)
    if post.curator_upvotes > post.curator_downvotes:
        post.approved = timezone.now()
    else:
        post.approved = None
    post.save()

    curator_type = ContentType.objects.get(app_label='manopozicija', model='curator')
    if post.content_type == curator_type:
        update_curator_application(post.content_object.user, post.topic, post.approved)

    return post.curator_upvotes, post.curator_downvotes


def update_curator_application(user, topic, approved):
    models.TopicCurator.objects.update_or_create(user=user, topic=topic, defaults={'approved': approved})


def get_user_topic_votes(user, topic):
    return dict(
        models.UserPostPosition.objects.
        filter(user=user, post__topic=topic).
        values_list('post_id', 'position')
    )


def get_curator_topic_votes(user, topic):
    return dict(
        models.PostLog.objects.
        filter(user=user, post__topic=topic, action=models.PostLog.VOTE).
        values_list('post_id', 'vote')
    )


def get_topic_curators(topic):
    return (
        models.Curator.objects.
        filter(user__topiccurator__topic=topic, user__topiccurator__approved__isnull=False).
        order_by('user__topiccurator__approved')
    )


def compare_positions(group, user):
    post_positions = (
        models.UserPostPosition.objects.
        filter(user=user, post__actor__ingroup=group).
        exclude(position=0).
        annotate(actor=F('post__actor')).
        values('user', 'actor').
        annotate(
            distance=ExpressionWrapper(Sum(Sqrt(Power(F('position') - 1, 2)) / 2), output_field=FloatField()),
            weight=Count('pk'),
        )
    )

    argument_positions = (
        models.UserArgumentPosition.objects.
        filter(user=user, argument__actorargumentposition__actor__ingroup=group).
        exclude(position=0).
        annotate(actor=F('argument__actorargumentposition__actor')).
        values('user', 'actor').
        annotate(
            distance=ExpressionWrapper((
                Sum(Sqrt(Power(F('position') - F('argument__actorargumentposition__position'), 2)) / 2)
            ), output_field=FloatField()),
            weight=Count('argument__actorargumentposition'),
        )
    )

    result = []

    key = lambda x: (x['user'], x['actor'])
    positions = sorted(itertools.chain(post_positions, argument_positions), key=key)
    groups = itertools.groupby(positions, key=key)
    for (user, actor), group in groups:
        group = list(group)
        value = sum(x['distance'] or 0 for x in group)
        weight = sum(x['weight'] or 1 for x in group)
        distance = value / weight
        result.append((actor, distance))

    # TODO: calculate post role positions (reuse ActorPostPosition model)
    # TODO: calculate positions for groups of actors

    return sorted(result, key=lambda x: (x[1], x[0]))


def get_user_quote_positions(group, user):
    return (
        models.UserPostPosition.objects.
        filter(user=user, post__actor__ingroup=group).
        values_list(
            'post__quote__source__actor',
            'post__position',
            'position',
        ).
        order_by('pk')
    )


def get_user_argument_positions(group, user):
    return (
        models.UserArgumentPosition.objects.
        filter(user=user, argument__actorargumentposition__actor__ingroup=group).
        values_list(
            'argument__title',
            'argument__actorargumentposition__actor',
            'argument__actorargumentposition__position',
            'position',
        ).
        order_by('argument__title', 'argument__actorargumentposition__actor')
    )


def get_user_event_positions(group, user):
    return (
        models.UserPostPosition.objects.
        filter(user=user, post__actorpostposition__actor__group=group).
        values_list(
            'post__actorpostposition__actor',
            'post__actorpostposition__position',
            'position',
        ).
        order_by('pk')
    )
