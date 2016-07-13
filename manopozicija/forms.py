from django import forms
from django.utils.translation import ugettext, ugettext_lazy as _

from manopozicija import models


class PersonForm(forms.ModelForm):

    class Meta:
        model = models.Actor
        fields = ('first_name', 'last_name', 'title', 'photo')


class GroupForm(forms.ModelForm):

    class Meta:
        model = models.Actor
        fields = ('first_name', 'title', 'photo')


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


class ArgumentForm(forms.ModelForm):
    position = forms.BooleanField(label=_("neigiamas"), required=False)

    class Meta:
        model = models.Argument
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
