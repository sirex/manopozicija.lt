import factory
import datetime

from django.conf import settings
from factory.django import DjangoModelFactory, ImageField

from allauth.account.models import EmailAddress

import manopozicija.models as mp


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
        model = mp.Indicator
        django_get_or_create = ('slug',)


class BodyFactory(DjangoModelFactory):
    name = 'Seimas'

    class Meta:
        model = mp.Body
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
        model = mp.Topic
        django_get_or_create = ('title',)

    @factory.post_generation
    def indicators(self, create, extracted, **kwargs):
        if create:
            self.indicators = extracted or [IndicatorFactory()]


class PartyActorFactory(DjangoModelFactory):
    first_name = 'Lietuvos Žaliųjų Partija'
    last_name = ''
    title = 'politinė partija'
    photo = ImageField()
    group = True
    body = factory.SubFactory(BodyFactory, name='Seimas')

    class Meta:
        model = mp.Actor
        django_get_or_create = ('first_name',)


class PersonActorFactory(DjangoModelFactory):
    first_name = 'Mantas'
    last_name = 'Adomėnas'
    title = ''
    photo = ImageField()
    group = False
    body = None

    class Meta:
        model = mp.Actor
        django_get_or_create = ('first_name', 'last_name')


class SourceFactory(DjangoModelFactory):
    actor = factory.SubFactory(PersonActorFactory)
    actor_title = 'seimo narys'
    source_title = 'kauno.diena.lt'
    source_link = 'http://kauno.diena.lt/naujienos/lietuva/politika/skinasi-kelia-balsavimas-internetu-740017'
    timestamp = datetime.datetime(2016, 3, 22, 16, 34, 0)
    position = -1

    class Meta:
        model = mp.Source
        django_get_or_create = ('source_link',)


class QuoteFactory(DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    source = factory.SubFactory(SourceFactory)
    text = 'Nepasiduokime paviršutiniškiems šūkiams – šiuolaikiška, modernu.'

    class Meta:
        model = mp.Quote


class ArgumentFactory(DjangoModelFactory):
    topic = factory.SubFactory(TopicFactory)
    quote = factory.SubFactory(QuoteFactory)
    title = 'šiuolaikiška, modernu'
    counterargument = None
    counterargument_title = ''
    position = 1

    class Meta:
        model = mp.Argument


class EventFactory(DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    type = mp.Event.DOCUMENT
    title = 'Balsavimo internetu koncepcijos patvirtinimas'
    source_title = 'e-seimas.lrs.lt'
    source_link = 'https://e-seimas.lrs.lt/portal/legalAct/lt/TAD/TAIS.287235?positionInSearchResults=0&searchModelUUID=eaee1625-cf9f-46c0-931c-482a218029e8'
    timestamp = datetime.datetime(2006, 11, 26)
    position = 0
    group = None

    class Meta:
        model = mp.Event
        django_get_or_create = ('title',)


class PostFactory(DjangoModelFactory):
    body = factory.SubFactory(BodyFactory, name='Seimas')
    topic = factory.SubFactory(TopicFactory)
    actor = factory.SubFactory(PersonActorFactory)
    position = 1
    approved = True
    timestamp = datetime.datetime(2016, 3, 22, 16, 34, 0)

    class Meta:
        model = mp.Post


class UserPositionFactory(DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    post = factory.SubFactory(PostFactory)
    position = 1

    class Meta:
        model = mp.UserPosition


def create_quote_agruments(topic, quote, arguments):
    result = []
    for position, argument, counterargument in arguments:
        counterargument_title = ''
        if counterargument is None:
            counterargument = False
        elif counterargument is not True:
            counterargument = True
            counterargument_title = counterargument
        argument = ArgumentFactory(
            topic=topic, quote=quote, position=position, title=argument,
            counterargument=counterargument, counterargument_title=counterargument_title,
        )
        result.append(argument)
    return result


def create_topic_quotes(topic, actor, title, source, date, quotes):
    result = []
    first_name, last_name = actor.split()
    timestamp = datetime.datetime.strptime(date, '%Y-%m-%d')
    actor = PersonActorFactory(first_name=first_name, last_name=last_name)
    source = SourceFactory(actor=actor, actor_title=title, source_title=source, timestamp=timestamp)
    for upvotes, downvotes, text, arguments in quotes:
        quote = QuoteFactory(text=text, source=source)
        create_quote_agruments(topic, quote, arguments)
        post = PostFactory(topic=topic, content_object=quote, upvotes=upvotes, timestamp=timestamp)
        result.append(post)
    return result


def create_topic_event(topic, upvotes, downvotes, title, source, date):
    timestamp = datetime.datetime.strptime(date, '%Y-%m-%d')
    event = EventFactory(type=mp.Event.DOCUMENT, title=title, source_title=source, timestamp=timestamp)
    return PostFactory(topic=topic, content_object=event, upvotes=upvotes, timestamp=timestamp)


def create_topic_posts(topic, posts):
    result = []
    for content_type, *args in posts:
        if content_type == 'event':
            result.append(create_topic_event(topic, *args))
        else:
            result.extend(create_topic_quotes(topic, *args))
    return result
