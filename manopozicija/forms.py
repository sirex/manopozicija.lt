from django import forms
from django.utils.translation import ugettext_lazy as _

import manopozicija.models as mp


class PersonForm(forms.ModelForm):

    class Meta:
        model = mp.Actor
        fields = ('first_name', 'last_name', 'title', 'photo')


class GroupForm(forms.ModelForm):

    class Meta:
        model = mp.Actor
        fields = ('first_name', 'title', 'photo')


class SourceForm(forms.ModelForm):

    class Meta:
        model = mp.Source
        fields = ('actor', 'source_link', 'timestamp')


class QuoteForm(forms.ModelForm):

    class Meta:
        model = mp.Quote
        fields = ('reference_link', 'text')
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3})
        }


class ArgumentForm(forms.ModelForm):
    position = forms.BooleanField(label=_("neigiamas"), required=False)

    class Meta:
        model = mp.Argument
        fields = ('title', 'position', 'counterargument', 'counterargument_title')
        labels = {'counterargument': _("kontrargumentas")}

    def clean_position(self):
        return -1 if self.cleaned_data['position'] else 1


class EventForm(forms.ModelForm):

    class Meta:
        model = mp.Event
        fields = ('title', 'source_link', 'source_title', 'timestamp')
