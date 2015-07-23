import autoslug

from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


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


class Position(models.Model):
    topic = models.ForeignKey('Topic')
    weight = models.SmallIntegerField(default=1)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


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
    name = models.CharField(max_length=255)
    link = models.URLField()
    fraction = models.CharField(max_length=255)
    position = models.PositiveSmallIntegerField(choices=POSITION_CHOICES, default=NO_VOTE)
    score = models.SmallIntegerField()

    def save(self, *args, **kw):
        if self.position is not None:
            self.score = self.SCORE_TABLE[self.position]
        return super().save(*args, **kw)
