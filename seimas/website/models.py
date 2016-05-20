import autoslug
import csv

from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from seimas.website.lists import professions


class Indicator(models.Model):
    slug = models.SlugField(unique=True, editable=False)
    created = CreationDateTimeField(editable=False)
    modified = ModificationDateTimeField(editable=False)
    deleted = models.DateTimeField(null=True, blank=True, editable=False)
    last_update = models.DateTimeField(null=True, blank=True, editable=False)
    update_freq = models.PositiveIntegerField(default=60 * 60 * 24, help_text=_(
        'Indicator update frequency in seconds (86400 == 1 day).'
    ))
    error_count = models.PositiveIntegerField(default=0, editable=False)
    traceback = models.TextField(blank=True, editable=False)
    title = models.CharField(max_length=255)
    ylabel = models.CharField(max_length=255)
    source = models.URLField(_("Šaltinis"))

    def __str__(self):
        return self.title


class Topic(models.Model):
    created = CreationDateTimeField()
    modified = ModificationDateTimeField()
    author = models.ForeignKey(User, null=True, blank=True)
    slug = autoslug.AutoSlugField(populate_from='title')
    title = models.CharField(_("Pavadinimas"), max_length=255)
    description = models.TextField(_("Aprašymas"), blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('topic-details', args=[self.slug])


class PersonManager(models.Manager):
    def get_or_create(self, name, meeting_id, meetings_file):
        name_args = name.split()
        first_name = None
        last_name = None
        person = None

        if name.lower() == 'pirmininkas':
            with meetings_file as csvfile:
                reader = csv.reader(csvfile, delimiter=';', quotechar='"')
                for meeting_args in reader:
                    name = meeting_args[14]
                    if meeting_args[0] == meeting_id:
                        break

        if len(name_args) == 3:
            raise ValueError('Name contains more than 2 words: ' + name)
        elif len(name_args) == 2:
            first_name = name_args[0].strip('.')
            last_name = name_args[1]
        elif len(name_args) == 1:
            last_name = name_args[0]

        try:
            person = Person.objects.get(name__contains=last_name)
        except Person.DoesNotExist:
            person = Person.objects.create(name=name)
        except Person.MultipleObjectsReturned:
            person = Person.objects.filter(name__contains=last_name).get(name__contains=first_name)
        return person


class Person(models.Model):
    PROFESSION_CHOICES = [('', 'Nenurodyta')] + [(profession, profession.title()) for profession in professions]

    slug = autoslug.AutoSlugField(populate_from='name')
    name = models.CharField(max_length=255)
    profession = models.CharField(max_length=64, blank=True, choices=PROFESSION_CHOICES)

    objects = PersonManager()

    def __str__(self):
        return self.name


class Position(models.Model):
    topic = models.ForeignKey('Topic')
    person = models.ForeignKey(Person, null=True, blank=True)
    weight = models.SmallIntegerField(default=1)   # visada 1 arba -1
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class Quote(models.Model):  # Laikraščio citata
    NONE = 0
    YEAR = 1
    MONTH = 2
    DAY = 3
    HOUR = 4
    MINUTE = 5
    SECOND = 6
    TIMESTAMP_DISPLAY_CHOICES = (
        (NONE, _('Nėra')),
        (YEAR, _('Metai')),
        (MONTH, _('Mėnuo')),
        (DAY, _('Diena')),
        (HOUR, _('Valanda')),
        (MINUTE, _('Minutė')),
        (SECOND, _('Sekundė')),
    )

    person = models.ForeignKey(Person)
    quote = models.TextField(_("Citata"))
    link = models.URLField(_("Nuoroda"), blank=True)
    source = models.CharField(_("Šaltinis"), max_length=255, blank=True)
    timestamp = models.DateTimeField(_("Data"), blank=True, null=True)
    timestamp_display = models.PositiveSmallIntegerField(choices=TIMESTAMP_DISPLAY_CHOICES, default=DAY)
    position = GenericRelation(Position, related_query_name='quote')
    title = models.CharField(_("Pavadinimas"), max_length=255)
    description = models.TextField(_("Aprašymas"), blank=True)


class Voting(models.Model):  # Klausimas dėl kurio balsuojama
    SEIMAS = 1
    SAVIVALDYBE = 2
    VOTING_TYPE_CHOICES = (
        (SEIMAS, _('Seimo')),
        (SAVIVALDYBE, _('Savivaldybės')),
    )
    created = CreationDateTimeField()
    modified = ModificationDateTimeField()
    author = models.ForeignKey(User, null=True, blank=True)
    title = models.CharField(_("Pavadinimas"), max_length=255)
    link = models.URLField(_("Nuoroda"))
    description = models.TextField(_("Aprašymas"), blank=True)
    datetime = models.DateTimeField(null=True, blank=True)
    vid = models.CharField(_("Balsavimo ID"), max_length=20, blank=True)
    question = models.CharField(_("Klausimas"), max_length=255, blank=True)
    question_a = models.CharField(_("Klausimas A"), max_length=255, blank=True)
    question_b = models.CharField(_("Klausimas B"), max_length=255, blank=True)
    result = models.CharField(_("Rezultatas"), max_length=40, blank=True)
    sitting_no = models.CharField(_("Posėdžio Nr."), max_length=40, blank=True)
    position = GenericRelation(Position, related_query_name='voting')
    voting_type = models.PositiveSmallIntegerField(choices=VOTING_TYPE_CHOICES, default=SAVIVALDYBE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('topic-details', args=[self.slug])

    def get_result_string(self):
        if self.question == '':
            if self.result == 'pritarta formuluotei A':
                return self.question_a
            elif self.result == 'pritarta formuluotei B':
                return self.question_b
        return self.result


class VoteManager(models.Manager):
    def get_vote_id(self, display_name):
        for choice, name in Vote.POSITION_CHOICES:
            if name.lower() == display_name.lower():
                return choice


class Vote(models.Model):  # Balsas už konkretų klausimą
    NO_VOTE = 0
    AYE = 1
    NO = 2
    ABSTAIN = 3
    POSITION_CHOICES = (
        (NO_VOTE, _('Nebalsavo')),
        (AYE, _('Už')),
        (NO, _('Prieš')),
        (ABSTAIN, _('Susilaikė')),
    )

    SCORE_TABLE = {
        AYE: 2,
        NO_VOTE: -1,
        ABSTAIN: -1,
        NO: -2,
    }

    voting = models.ForeignKey(Voting)
    person = models.ForeignKey(Person, null=True, blank=True)
    name = models.CharField(max_length=255)
    link = models.URLField()
    fraction = models.CharField(max_length=255)
    vote = models.PositiveSmallIntegerField(choices=POSITION_CHOICES, default=NO_VOTE)
    score = models.SmallIntegerField()
    position = GenericRelation(Position, related_query_name='vote')

    objects = VoteManager()

    def save(self, *args, **kw):
        if self.position is not None:
            self.score = self.SCORE_TABLE[self.vote]
        return super().save(*args, **kw)
