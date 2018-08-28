import io
import factory
import datetime


from PIL import Image
from django.conf import settings
from factory.django import DjangoModelFactory, ImageField
from django.utils import timezone

from allauth.account.models import EmailAddress

from manopozicija import models
from manopozicija import services


class EmailAddressFactory(DjangoModelFactory):
    email = factory.SelfAttribute('user.email')
    verified = True
    primary = True

    class Meta:
        model = EmailAddress
        django_get_or_create = ('email',)


class UserFactory(DjangoModelFactory):
    first_name = 'Vardenis'
    last_name = 'Pavardenis'
    username = factory.LazyAttribute(lambda x: x.first_name.lower())
    email = factory.LazyAttribute(lambda x: '%s.%s@example.com' % (x.first_name.lower(), x.last_name.lower()))
    is_active = True
    emailaddress = factory.RelatedFactory(EmailAddressFactory, 'user')

    class Meta:
        model = settings.AUTH_USER_MODEL
        django_get_or_create = ('email',)


class IndicatorFactory(DjangoModelFactory):
    slug = 'voter-turnout'
    title = 'Rinkimuose dalyvavusių rinkėjų skaičius, palyginti su visų rinkėjų skaičiumi'
    ylabel = 'Aktyvumas procentais'
    source = 'http://ec.europa.eu/eurostat/tgm/table.do?tab=table&init=1&language=en&pcode=tsdgo310&plugin=1'

    class Meta:
        model = models.Indicator
        django_get_or_create = ('slug',)


class BodyFactory(DjangoModelFactory):
    name = 'Seimas'

    class Meta:
        model = models.Body
        django_get_or_create = ('name',)


class TermFactory(DjangoModelFactory):
    body = factory.SubFactory(BodyFactory, name='Seimas')
    since = datetime.datetime(2012, 10, 14)
    until = datetime.datetime(2016, 10, 9)


class TopicFactory(DjangoModelFactory):
    title = 'Balsavimas internetu'
    description = ''
    logo = ImageField(filename='logo.png', **settings.MANOPOZICIJA_TOPIC_LOGO_SIZE._asdict())
    default_body = factory.SubFactory(BodyFactory, name='Seimas')

    class Meta:
        model = models.Topic
        django_get_or_create = ('title',)

    @factory.post_generation
    def indicators(self, create, extracted, **kwargs):
        if create:
            self.indicators.set(extracted or [IndicatorFactory()])


class PartyActorFactory(DjangoModelFactory):
    first_name = 'Lietuvos Žaliųjų Partija'
    last_name = ''
    title = 'politinė partija'
    photo = ImageField()
    group = True
    body = factory.SubFactory(BodyFactory, name='Seimas')

    class Meta:
        model = models.Actor
        django_get_or_create = ('first_name',)


class PersonActorFactory(DjangoModelFactory):
    first_name = 'Mantas'
    last_name = 'Adomėnas'
    title = 'seimo narys'
    photo = ImageField()
    group = False
    body = None

    class Meta:
        model = models.Actor
        django_get_or_create = ('first_name', 'last_name')


class PostFactory(DjangoModelFactory):
    body = factory.SubFactory(BodyFactory, name='Seimas')
    topic = factory.SubFactory(TopicFactory)
    actor = factory.SubFactory(PersonActorFactory)
    position = 1
    approved = datetime.datetime(2016, 3, 22, 16, 34, 0)
    timestamp = datetime.datetime(2016, 3, 22, 16, 34, 0)

    class Meta:
        model = models.Post


class SourceFactory(DjangoModelFactory):
    actor = factory.SubFactory(PersonActorFactory)
    actor_title = 'seimo narys'
    source_title = 'kauno.diena.lt'
    source_link = 'http://kauno.diena.lt/naujienos/lietuva/politika/skinasi-kelia-balsavimas-internetu-740017'
    timestamp = datetime.datetime(2016, 3, 22, 16, 34, 0)
    position = -1

    class Meta:
        model = models.Source
        django_get_or_create = ('source_link',)


class QuoteFactory(DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    source = factory.SubFactory(SourceFactory)
    text = 'Nepasiduokime paviršutiniškiems šūkiams – šiuolaikiška, modernu.'

    class Meta:
        model = models.Quote


class ArgumentFactory(DjangoModelFactory):
    topic = factory.SubFactory(TopicFactory)
    title = 'šiuolaikiška, modernu'

    class Meta:
        model = models.Argument
        django_get_or_create = ('topic', 'title')


class PostArgumentFactory(DjangoModelFactory):
    topic = factory.SubFactory(TopicFactory)
    post = factory.SubFactory(PostFactory)
    quote = factory.SubFactory(QuoteFactory)
    title = 'šiuolaikiška, modernu'
    counterargument = None
    counterargument_title = ''
    position = 1

    class Meta:
        model = models.PostArgument

    @factory.post_generation
    def argument(self, create, extracted, **kwargs):
        if create:
            ArgumentFactory(topic=self.topic, title=self.title)


class EventFactory(DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    type = models.Event.DOCUMENT
    title = 'Balsavimo internetu koncepcijos patvirtinimas'
    source_title = 'e-seimas.lrs.lt'
    source_link = 'https://e-seimas.lrs.lt/portal/legalAct/lt/TAD/TAIS.287235?positionInSearchResults=0&searchModelUUID=eaee1625-cf9f-46c0-931c-482a218029e8'
    timestamp = datetime.datetime(2006, 11, 26)
    position = 0
    group = None

    class Meta:
        model = models.Event
        django_get_or_create = ('title',)


class UserPositionFactory(DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    post = factory.SubFactory(PostFactory)
    position = 1

    class Meta:
        model = models.UserPostPosition


class CuratorFactory(DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    actor = None
    title = 'visuomenės veikėjas'
    photo = ImageField()

    class Meta:
        model = models.Curator
        django_get_or_create = ('user',)


class TopicCuratorFactory(DjangoModelFactory):
    approved = datetime.datetime(2016, 3, 22, 16, 34, 0)
    topic = factory.SubFactory(TopicFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = models.TopicCurator
        django_get_or_create = ('user', 'topic')


class GroupFactory(DjangoModelFactory):
    title = 'Kandidatai į 2016 metų Seimą'
    timestamp = datetime.datetime(2006, 11, 26)

    class Meta:
        model = models.Group
        django_get_or_create = ('title',)

    @factory.post_generation
    def members(self, create, extracted, **kwargs):
        if create:
            for member in extracted:
                self.members.add(member)


def _prep_quote_arguments(arguments):
    result = []
    for position, argument, counterargument in arguments:
        counterargument_title = ''
        if counterargument is None:
            counterargument = False
        elif counterargument is not True:
            counterargument = True
            counterargument_title = counterargument
        result.append({
            'title': argument,
            'position': position,
            'counterargument': counterargument,
            'counterargument_title': counterargument_title,
        })
    return result


def create_quote_agruments(topic, quote, post, arguments):
    result = []
    for data in _prep_quote_arguments(arguments):
        argument = PostArgumentFactory(topic=topic, quote=quote, post=post, **data)
        result.append(argument)
    return result


def _get_source_link(source, date):
    return 'http://%s/%s' % (source, date.replace('-', '/'))


def create_topic_quotes(topic, user, actor, title, source, date, quotes):
    result = []
    user = user or UserFactory()
    first_name, last_name = actor.split()
    actor = PersonActorFactory(first_name=first_name, last_name=last_name)
    source = {
        'actor': actor,
        'source_link': _get_source_link(source, date),
        'timestamp': datetime.datetime.strptime(date, '%Y-%m-%d'),
    }
    for upvotes, downvotes, text, arguments in quotes:
        quote = {
            'text': text,
            'reference_link': '',
        }
        quote = services.create_quote(user, topic, source, quote, _prep_quote_arguments(arguments))
        post = quote.post.first()

        position = 1 if upvotes > downvotes else -1 if upvotes < downvotes else 0
        services.update_user_position(user, post, position)

        result.append(post)

    return result


def create_topic_event(topic, user, upvotes, downvotes, title, source, date):
    user = user or UserFactory()
    timestamp = datetime.datetime.strptime(date, '%Y-%m-%d')
    event = services.create_event(user, topic, {
        'type': models.Event.DOCUMENT,
        'title': title,
        'source_link': _get_source_link(source, date),
        'source_title': source,
        'timestamp': timestamp,
    })
    post = event.post.first()
    position = 1 if upvotes > downvotes else -1 if upvotes < downvotes else 0
    services.update_user_position(user, post, position)
    return post


def create_topic_curator(topic, user, name, title):
    user_data = {}
    user_data['first_name'], user_data['last_name'] = name.split()
    curator = services.create_curator(user, topic, user_data, {
        'title': title,
        'photo': None,
    })
    post = curator.posts.first()
    return post


def create_topic_posts(topic, user, posts):
    result = []
    user = user or UserFactory()
    for content_type, *args in posts:
        if content_type == 'event':
            result.append(create_topic_event(topic, user, *args))
        elif content_type == 'curator':
            result.append(create_topic_curator(topic, user, *args))
        else:
            result.extend(create_topic_quotes(topic, user, *args))
    return result


def create_arguments(topic, arguments, approved=True):
    result = []
    approved = timezone.now() if approved else None
    for position, counterargument, argument in arguments:
        quote = QuoteFactory()
        post = PostFactory(topic=topic, content_object=quote, approved=approved)
        argument = PostArgumentFactory(
            topic=topic, post=post, quote=quote,
            position=position, title=argument, counterargument=counterargument,
        )
        result.append(argument)
    return result


def get_quote_form_data(**kwargs):
    source = {
        'actor': PersonActorFactory(),
        'source_link': 'http://kauno.diena.lt/naujienos/lietuva/politika/skinasi-kelia-balsavimas-internetu-740017',
        'timestamp': datetime.datetime(2016, 3, 22, 16, 34, 0),
    }
    quote = {
        'reference_link': '',
        'text': kwargs.get('text', 'Nepasiduokime paviršutiniškiems šūkiams – šiuolaikiška, modernu.'),
    }
    arguments = [
        {
            'title': 'šiuolaikiška, modernu',
            'position': 1,
            'counterargument': True,
            'counterargument_title': '',
        }
    ]
    return source, quote, arguments


def get_image_bytes(width=100, height=100, format='JPEG', color='black'):
    image = Image.new('RGB', (width, height), color)
    output = io.BytesIO()
    image.save(output, format=format)
    return output.getvalue()
