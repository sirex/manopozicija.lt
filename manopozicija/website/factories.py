import factory

from django.conf import settings
from factory.django import DjangoModelFactory, ImageField

from allauth.account.models import EmailAddress

from manopozicija.website.models import Indicator, Topic


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
    email = factory.LazyAttribute(lambda x: '%s@example.com' % x.username)
    is_active = True
    emailaddress = factory.RelatedFactory(EmailAddressFactory, 'user')

    class Meta:
        model = settings.AUTH_USER_MODEL
        django_get_or_create = ('username',)


class IndicatorFactory(DjangoModelFactory):
    slug = 'voter-turnout'
    title = 'Rinkimuose dalyvavusių rinkėjų skaičius, palyginti su visų rinkėjų skaičiumi'
    ylabel = 'Aktyvumas procentais'
    source = 'http://ec.europa.eu/eurostat/tgm/table.do?tab=table&init=1&language=en&pcode=tsdgo310&plugin=1'

    class Meta:
        model = Indicator


class TopicFactory(DjangoModelFactory):
    author = factory.SubFactory(UserFactory, username='vardenis')
    title = 'Balsavimas internetu'
    description = ''
    logo = ImageField(filename='logo.png', **settings.MANOPOZICIJA_TOPIC_LOGO_SIZE._asdict())

    class Meta:
        model = Topic
        django_get_or_create = ('title',)

    @factory.post_generation
    def indicators(self, create, extracted, **kwargs):
        if create:
            self.indicators = extracted or [IndicatorFactory()]
