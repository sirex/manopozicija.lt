import autoslug

from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from sorl.thumbnail import ImageField

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Body(models.Model):
    """Government body

    Currently supported government body is Lithuanian parliament.

    Attributes
    ----------

    name : str
        Name of government body.

    """
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Term(models.Model):
    """Government body term of office

    This is a period of time for each government body between elections.
    For example Lithuanian parliament as term of four years.

    """
    body = models.ForeignKey(Body)
    since = models.DateTimeField()
    until = models.DateTimeField()


class Indicator(models.Model):
    """Key performance indicators

    Key performance indicators are data sources plotted on the topic
    diagram, showing how government impacts certain indicators.

    """
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
    """A political topic

    Political topic is a point of interest around a topic.

    Attributes
    ----------

    default_body : Body
        Many government bodies can work on a same topic, but usually one
        topic is bound to a particular government body. This parameter
        specifies which political body is most relevant for this topic.

    """
    created = CreationDateTimeField()
    slug = autoslug.AutoSlugField(populate_from='title')
    title = models.CharField(_("Pavadinimas"), max_length=255)
    description = models.TextField(_("Aprašymas"), blank=True)
    indicators = models.ManyToManyField(Indicator, blank=True)
    default_body = models.ForeignKey(Body)
    logo = ImageField(upload_to='topics/%Y/%m/%d/', blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('topic-details', args=[self.pk, self.slug])


class Actor(models.Model):
    """A public person or group of people like a political party

    Attributes
    ----------

    first_name : str
        First person's name or name of a group.

    last_name : str
        Last person's name or empty string if actor is a group.

    title : str
        Person's domain of interest of group type.

    """
    first_name = models.CharField(_("Vardas"), max_length=255)
    last_name = models.CharField(_("Pavardė"), max_length=255)
    title = models.CharField(_("Autoriaus sritis"), max_length=255, help_text=_(
        "Autoriaus profesija arba domėjimosi sritis atitinkanti citatos tekstą."
    ))
    photo = ImageField(_("Nuotrauka"), upload_to='actors/%Y/%m/%d/', blank=True)
    group = models.BooleanField(default=False)
    body = models.ForeignKey(Body, blank=True, null=True)  # required only for group

    def __str__(self):
        return ' '.join([self.first_name, self.last_name])


class Member(models.Model):
    """Actor's membership in a group"""
    actor = models.ForeignKey(Actor, related_name='+')
    group = models.ForeignKey(Actor)
    since = models.DateTimeField()
    until = models.DateTimeField()


class Post(models.Model):
    """Topic's timeline posts.

    Attributes
    ----------

    body : Body
        Government body where this object can be shown.

    topic : Topic
        Post topic.

    actor : Actor
        Actor of the content object if object has an actor.

    approved : datetime.datetime
        Indicates when this post was approved by a topic curator.

    content_object : Event | Quote | Curator
        An object associated with this post.

    timestamp : datetime.datetime
        Timestamp of content_object.

    position : float
        Actor's position of a quote.

    upvotes : int
        Number of users who upvoted this post.

    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    body = models.ForeignKey(Body)
    topic = models.ForeignKey('Topic')
    actor = models.ForeignKey(Actor, null=True, blank=True)
    position = models.FloatField()
    approved = models.DateTimeField(null=True, blank=True)
    timestamp = models.DateTimeField()
    upvotes = models.PositiveIntegerField(default=0)
    downvotes = models.PositiveIntegerField(default=0)
    curator_upvotes = models.PositiveIntegerField(default=0)
    curator_downvotes = models.PositiveIntegerField(default=0)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ('topic', 'content_type', 'object_id')

    def __str__(self):
        return '%s: %s' % (self.content_type, self.object_id)


class Curator(models.Model):
    """User who is a curator of one or more topics

    Attributes
    ----------

    title : str
        Person's domain of interest of group type.

    post : Post
        First topic curators have to wait in queue while other curators
        approves his request to become new topic curator.

        Each new curator request is created as a post.

    """
    user = models.OneToOneField(User)
    actor = models.ForeignKey(Actor, null=True, blank=True)
    title = models.CharField(max_length=255)
    photo = ImageField(upload_to='actors/%Y/%m/%d/')
    posts = GenericRelation(Post)


class TopicCurator(models.Model):
    """Topic curators

    Attributes
    ----------

    approved : bool
        Time when this topic curator was approved by others.

    """
    created = models.DateTimeField(auto_now_add=True)
    approved = models.DateTimeField(null=True, blank=True)
    topic = models.ForeignKey(Topic)
    user = models.ForeignKey(User)


class PostLog(models.Model):
    """Log of all actions performed with a post.

    Each curator can vote if new curator or suggested new post for the
    timeline should be approved.

    Attributes
    ----------

    created : datetime.datetime
        When vote has been given.

    curator : Curator
        Who voted.

    post : Post
        A topic post voted for.

    vote : int
        Positive or negative integer as vote value.

    """
    VOTE = 1
    ACTION_CHOICES = (
        (VOTE, _("balsavo")),
    )

    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)
    post = models.ForeignKey(Post)
    action = models.PositiveSmallIntegerField(choices=ACTION_CHOICES)
    vote = models.SmallIntegerField(null=True, blank=True)


class Reference(models.Model):
    """Topic positions referring to specific events.

    One event can refer to other events.

    For example, first comes the bill, then a voting. Voting event,
    can refer to one or more bills voted for.

    Also a quote can directly refer to a specific event (for example
    a document).

    Attributes
    ----------

    event : Event
        Event referred to.

    content_object : Event | Quote
        An object referring to the event.

    """
    event = models.ForeignKey('Event')

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class Event(models.Model):
    """An event in a topic.

    Event should indicate an action taken by a government body that
    addresses a topic in question.

    Event can be a new bill, a voting or any other action.

    Attributes
    ----------

    user : User
        User who suggested this event.

    type : int
        Event type. Usually event type is inferred from source link.

    title : str
        Short title describing event in a human readable form.
        Bureaucratic formulations should be avoided.

    source_title : str
        If source title is left empty and source link is a URL, then
        source title will automatically be filled with the domain of the
        URL.

        But this can be overridden by specifying different source title.

    source_link : str
        Can be a URL or in rare cases a textual description pointing to
        a book, paper, journal, etc. URL should be always preferred if
        available.

    timestamp : datetime.datetime
        Time, when this event happened.

    post : Post
        Events are shown in the topic timeline as posts.

    position : float
        Usually events does not have a position, but actors have a
        position about an event expressed via roles.

        So event position is just an outcome of actors positions that
        have a voting role in this event. If there is no voting for this
        event, it's position value stays zero.

    group : Event
        If set, tells that this event is part a group containing
        multiple events combined into one event.

        If event is in a group, it is not shown in the main topic event
        feed.

    """
    VOTING = 1
    DOCUMENT = 2
    TYPE_CHOICES = (
        (VOTING, _("Balsavimas")),
        (DOCUMENT, _("Teisės aktas")),
    )

    user = models.ForeignKey(User)
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES)
    title = models.CharField(_("Pavadinimas"), max_length=255)
    source_link = models.URLField(_("Šaltinio nuoroda"), max_length=255, blank=True, unique=True)
    source_title = models.CharField(_("Šaltinio antraštė"), max_length=255, blank=True)
    timestamp = models.DateTimeField(_("Kada buvo priimtas sprendimas?"))
    post = GenericRelation(Post, related_query_name='event')
    position = models.FloatField()
    references = GenericRelation(Reference, related_query_name='event')
    group = models.ForeignKey('self', null=True, blank=True)

    def validate_unique(self, exclude=None):
        # We want database level constraints, but don't want forms to validate source_link uniqueness.
        exclude = exclude or []
        exclude.extend(['source_link'])
        super().validate_unique(exclude)


class Role(models.Model):
    """Actor's role and position in an event.

    Events can have many actors involved in different ways. For example
    if event is a voting, then there can be many actors who voted whose
    role would be a voter.

    If event is a document, then there can be actors who proposed or
    created this document.

    Attributes
    ----------

    event : Event
        Event in which actor has a role.

    role : int
        What role did the actor had in an event.

    position : float
        Position of an actor about an event.

    """
    VOTED = 1  # an actor voted in a voting event
    PROPOSED = 2  # an actor proposed a document
    ROLE_CHOICES = (
        (VOTED, _("Balsavo")),
        (PROPOSED, _("Teikė")),
    )

    actor = models.ForeignKey(Actor)
    event = models.ForeignKey(Event)
    role = models.SmallIntegerField(choices=ROLE_CHOICES)
    position = models.FloatField()


class Source(models.Model):
    """Source of a quote.

    Attributes
    ----------

    actor : Actor
        An actor who is the author of a quote from this source.

    actor_title : str
        A domain of an actor in this source. One actor can work in
        different domains and can express his opinion as and expert of
        different domains.

        If actor is a group, then actor title can be left blank, it will
        be taken from Actor.title.

    source_link : str
        URL to the source material.

    source_title : str
        If source title is left empty, then source title will
        automatically be filled with the domain of the URL.

        But this can be overridden by specifying different source title.

    timestamp : datetime.datetime
        Time, when this source was published.

    position : float
        Average position calculated from assigned arguments.

    """
    actor = models.ForeignKey(Actor, verbose_name=_("Citatos autorius"))
    actor_title = models.CharField(_("Autoriaus veiklos sritis"), max_length=64, blank=True, help_text=_(
        "Autoriaus profesija arba domėjimosi sritis atitinkanti citatos tekstą."
    ))
    source_link = models.URLField(_("Šaltinio nuoroda"), max_length=255)
    source_title = models.CharField(_("Šaltinio antraštė"), max_length=255, blank=True)
    timestamp = models.DateTimeField(_("Kada paskelbtas šaltinis?"))
    position = models.FloatField(default=0)

    class Meta:
        unique_together = ('actor', 'source_link')

    def validate_unique(self, exclude=None):
        # We want database level constraints, but don't want forms to validate actor and source_link uniqueness.
        exclude = exclude or []
        exclude.extend(['actor', 'source_link'])
        super().validate_unique(exclude)


class Quote(models.Model):
    """A quote from an actor posted in a public source.

    Attributes
    ----------

    user : User
        A user who suggested this quote.

    source : Source
        A public source, where this comment was published. If not
        specified it means that source is unknown. Usually unknown
        source should be always specified unless source is really
        unknown

    reference_link : str
        Should be same link as in Event.source_link and if matching
        Event.source_link is found, Reference instance will be created
        pointing this quote to matching Event.

    """
    user = models.ForeignKey(User)
    source = models.ForeignKey(Source, null=True, blank=True)
    reference_link = models.URLField(_("Cituojamo šaltinio nuoroda"), blank=True, help_text=_(
        "Nuoroda į šaltinį, apie kurį autorius kalba savo citatoje."
    ))
    text = models.TextField(_("Citatos tekstas"), help_text=_(
        "Citatos tekste turėtų būti išreikšta viena mintis. Stenkitės citatos tekstą išlaikyti kiek galima trumpesnį."
    ))
    post = GenericRelation(Post, related_query_name='quote')
    references = GenericRelation(Reference, related_query_name='quote')

    def __str__(self):
        limit = 72
        if len(self.text) > limit:
            return self.text[:limit]
        else:
            return self.text


class Argument(models.Model):
    topic = models.ForeignKey(Topic)
    title = models.CharField(max_length=255)  # Same as PostArgument.title

    class Meta:
        unique_together = ('topic', 'title')


class PostArgument(models.Model):
    """Short tag uniquely identifying an argument.

    Multiple quotes can refer to the same argument, but in different
    words or can come from different actors and different sources.
    Tagging quotes with arguments helps to identify main ideas behind
    that quote and helps to better organize quotes.

    Attributes
    ----------

    counterargument : bool
        Event if positive attribute value indicates, that an argument is
        positive about a topic, but quote can criticise it's
        positiveness making quote itself negative, while general
        argument stays positive.

    counterargument_title : str
        Counterarguments also can be tagged with  short textual
        identifiers.

    position : int
        Each quote argument relates to a topic, it can be positive or
        negative. Positive argument indicates positive aspect of a
        topic.

        Final position value can be inverted if counterargument is True.

    """
    topic = models.ForeignKey(Topic)
    post = models.ForeignKey(Post)
    quote = models.ForeignKey(Quote)
    title = models.CharField(max_length=255)
    counterargument = models.BooleanField(_("Kontrargumentas"), default=False, blank=True)
    counterargument_title = models.CharField(max_length=255, blank=True)
    position = models.SmallIntegerField(default=0)

    def __str__(self):
        return '%s: %s' % (self.quote_id, self.title)


class ActorPostPosition(models.Model):
    actor = models.ForeignKey(Actor)
    post = models.ForeignKey(Post)
    position = models.FloatField(default=0)

    class Meta:
        unique_together = ('actor', 'post')


class ActorArgumentPosition(models.Model):
    actor = models.ForeignKey(Actor)
    argument = models.ForeignKey(Argument)
    position = models.FloatField(default=0)

    class Meta:
        unique_together = ('actor', 'argument')


class UserPostPosition(models.Model):
    """User position about a topic post.

    Each user can express their own position to a Quote or Event.

    Attributes
    ----------

    post : Post
        A post.

    position : int
        Value usually is -1, 0 or 1.

    """
    user = models.ForeignKey(User)
    post = models.ForeignKey(Post)
    position = models.SmallIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'post')


class UserArgumentPosition(models.Model):
    user = models.ForeignKey(User)
    argument = models.ForeignKey(Argument)
    position = models.FloatField(default=0)

    class Meta:
        unique_together = ('user', 'argument')
