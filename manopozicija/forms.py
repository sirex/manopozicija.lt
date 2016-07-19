from django import forms
from django.db.models import Value
from django.contrib.auth.models import User
from django.utils.translation import ugettext, ugettext_lazy as _

from manopozicija import models
from manopozicija.db import Similarity


class CombinedForms(object):

    def __init__(self, **forms_):
        self._forms = forms_

    def __getitem__(self, key):
        return self._forms[key]

    def is_valid(self):
        return all([f.is_valid() for f in self.forms])

    @property
    def cleaned_data(self):
        return {k: f.cleaned_data if f else None for k, f in self._forms.items()}

    @property
    def forms(self):
        return [f for f in self._forms.values() if f]


class PersonForm(forms.ModelForm):

    class Meta:
        model = models.Actor
        fields = ('first_name', 'last_name', 'title', 'photo')


class GroupForm(forms.ModelForm):

    class Meta:
        model = models.Actor
        fields = ('first_name', 'title', 'photo')
        labels = {
            'first_name': _("Pavadinimas"),
            'title': _("Grupės tipas"),
        }


class SourceForm(forms.ModelForm):

    class Meta:
        model = models.Source
        fields = ('actor', 'source_link', 'timestamp')


class QuoteForm(forms.ModelForm):

    class Meta:
        model = models.Quote
        fields = ('reference_link', 'text')
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3})
        }

    def __init__(self, topic, actor, source_link, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.topic = topic
        self.actor = actor
        self.source_link = source_link

    def clean_text(self):
        text = self.cleaned_data['text']
        if text and self.actor and self.source_link:
            quote = None
            source = models.Source.objects.filter(actor=self.actor, source_link=self.source_link).first()
            if source:
                quote = (
                    models.Quote.objects.
                    annotate(similarity=Similarity('text', Value(text))).
                    filter(source=source, similarity__gt=0.9).
                    first()
                )
            if quote and models.Post.objects.filter(topic=self.topic, quote=quote).exists():
                raise forms.ValidationError(ugettext("Toks komentaras jau yra įtrauktas į „%s“ temą.") % self.topic)
        return text


class ArgumentForm(forms.ModelForm):
    position = forms.BooleanField(label=_("neigiamas"), required=False)

    class Meta:
        model = models.PostArgument
        fields = ('title', 'position', 'counterargument', 'counterargument_title')
        labels = {'counterargument': _("kontrargumentas")}

    def clean_position(self):
        return -1 if self.cleaned_data['position'] else 1


class EventForm(forms.ModelForm):

    class Meta:
        model = models.Event
        fields = ('title', 'source_link', 'timestamp')

    def __init__(self, topic, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.topic = topic

    def clean_source_link(self):
        source_link = self.cleaned_data['source_link']
        if source_link:
            event = models.Event.objects.filter(source_link=source_link).first()
            if event and models.Post.objects.filter(topic=self.topic, event=event).exists():
                raise forms.ValidationError(ugettext("Toks sprendimas jau yra įtrauktas į „%s“ temą.") % self.topic)
        return source_link


class CuratorUserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class CuratorForm(forms.ModelForm):

    class Meta:
        model = models.Curator
        fields = ('title', 'photo')


class VoteForm(forms.Form):
    vote = forms.IntegerField(min_value=-1, max_value=1)

    def clean_vote(self):
        vote = self.cleaned_data['vote']
        if vote is None:
            return vote
        elif vote > 0:
            return 1
        elif vote < 0:
            return -1
        else:
            return 0
