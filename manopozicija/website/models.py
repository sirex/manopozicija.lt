import autoslug

from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Body(models.Model):
    name = models.CharField(max_length=255)


class Term(models.Model):
    body = models.ForeignKey(Body)
    since = models.DateTimeField()
    until = models.DateTimeField()


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
    slug = autoslug.AutoSlugField(populate_from='title')
    title = models.CharField(_("Pavadinimas"), max_length=255)
    description = models.TextField(_("Aprašymas"), blank=True)
    indicators = models.ManyToManyField(Indicator, blank=True)
    default_body = models.ForeignKey(Body)
    logo = models.ImageField(upload_to='topics/%Y/%m/%d/', blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('topic-details', args=[self.slug])


class Actor(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='actors/%Y/%m/%d/', blank=True)
    group = models.BooleanField(default=False)
    body = models.ForeignKey(Body, blank=True, null=True)  # required only for group

    def __str__(self):
        return ' '.join(self.first_name, self.last_name)


class Member(models.Model):
    actor = models.ForeignKey(Actor)
    group = models.ForeignKey(Actor)
    since = models.DateTimeField()
    until = models.DateTimeField()


class Curator(models.Model):
    user = models.ForeignKey(User)
    actor = models.ForeignKey(Actor, null=True, blank=True)
    title = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='actors/%Y/%m/%d/')


class CuratorQueueItem(models.Model):
    topic = models.ForeignKey('Topic')

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class TopicCurator(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    topic = models.ForeignKey('Topic')
    curator = models.ForeignKey(Curator)
    approved = models.BooleanField(default=False)  # approved by topic curators
    queue = GenericRelation(CuratorQueueItem)


class CuratorApproval(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    curator = models.ForeignKey(Curator)
    item = models.ForeignKey(CuratorQueueItem)
    value = models.SmallIntegerField()


class ActorPosition(models.Model):
    body = models.ForeignKey(Body)
    topic = models.ForeignKey('Topic')
    actor = models.ForeignKey(Actor, null=True, blank=True)
    value = models.SmallIntegerField()
    queue = GenericRelation(CuratorQueueItem)
    approved = models.BooleanField(default=False)  # approved by topic curators

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # denormalized fields
    timestamp = models.DateTimeField()


class UserPosition(models.Model):
    user = models.ForeignKey(User)
    actor_position = models.ForeignKey(ActorPosition)
    value = models.SmallIntegerField()


class Source(models.Model):
    actor = models.ForeignKey(Actor)
    actor_title = models.CharField(max_length=64, blank=True)
    source_title = models.CharField(_("Šaltinio antraštė"), max_length=255, blank=True)
    source_link = models.CharField(_("Šaltinio nuoroda"), max_length=255, blank=True)
    timestamp = models.DateTimeField(_("Data, laikas"))


class Quote(models.Model):
    user = models.ForeignKey(User)  # User who suggested this quote
    source = models.ForeignKey(Source)
    event_link = models.URLField(_("Nuoroda"), blank=True)
    quote = models.TextField(_("Citata"))


class Argument(models.Model):
    quote = models.ForeignKey(Quote)
    title = models.CharField(max_length=255)
    position = GenericRelation(ActorPosition, related_query_name='argument')


class Role(models.Model):
    VOTED = 1  # an actor voted in a voting event
    PROPOSED = 2  # an actor proposed a document
    ROLE_CHOICES = (
        (VOTED, _("Balsavo")),
        (PROPOSED, _("Teikė")),
    )

    role = models.SmallIntegerField(choices=ROLE_CHOICES)
    actor = models.ForeignKey(Actor)
    position = GenericRelation(ActorPosition, related_query_name='role')

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class Document(models.Model):
    title = models.CharField(max_length=255)
    source_link = models.CharField(_("Šaltinio nuoroda"), max_length=255, blank=True)
    timestamp = models.DateTimeField(_("Data, laikas"))
    position = GenericRelation(ActorPosition, related_query_name='document')
    roles = GenericRelation(Role, related_query_name='document')


class Event(models.Model):
    VOTING = 1
    TYPE_CHOICES = (
        (VOTING, _("Balsavimas")),
    )

    user = models.ForeignKey(User)  # User who suggested this event
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    source_title = models.CharField(_("Šaltinio antraštė"), max_length=255, blank=True)
    source_link = models.CharField(_("Šaltinio nuoroda"), max_length=255, blank=True)
    timestamp = models.DateTimeField(_("Data, laikas"))
    documents = models.ManyToManyField('Document')
    position = GenericRelation(ActorPosition, related_query_name='event')
    roles = GenericRelation(Role, related_query_name='event')
