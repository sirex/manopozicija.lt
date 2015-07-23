import autoslug

from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from seimas.website.lists import professions


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


class Person(models.Model):
    PROFESSION_CHOICES = [('', 'Nenurodyta')] + [(profession, profession.title()) for profession in professions]

    slug = autoslug.AutoSlugField(populate_from='name')
    name = models.CharField(max_length=255)
    profession = models.CharField(max_length=64, blank=True, choices=PROFESSION_CHOICES)

    def __str__(self):
        return self.title


class Position(models.Model):
    topic = models.ForeignKey('Topic')
    person = models.ForeignKey(Person, null=True, blank=True)
    weight = models.SmallIntegerField(default=1)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class Quote(models.Model):
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
    timestamp_display = models.PositiveSmallIntegerField(choices=TIMESTAMP_DISPLAY_CHOICES)
    position = GenericRelation(Position, related_query_name='quote')


class Voting(models.Model):
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


class Vote(models.Model):
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

    def save(self, *args, **kw):
        if self.position is not None:
            self.score = self.SCORE_TABLE[self.vote]
        return super().save(*args, **kw)
