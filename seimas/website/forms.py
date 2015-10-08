from django import forms
from django.utils.translation import ugettext

from seimas.website.models import Voting, Topic
from seimas.website.parsers.votings import get_voting_id


class NewVotingForm(forms.ModelForm):
    weight = forms.IntegerField(initial=1)

    class Meta:
        model = Voting
        fields = ('title', 'link', 'weight', 'description')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 16}),
        }

    def __init__(self, topic, *args, **kw):
        self.topic = topic
        super().__init__(*args, **kw)

    def clean_link(self):
        link = self.cleaned_data.get('link')
        vid = get_voting_id(link)
        if Voting.objects.filter(position__topic=self.topic, vid=vid).exists():
            raise forms.ValidationError(ugettext('Šis balsavimas jau yra pridėtas.'))
        return link


class TopicForm(forms.ModelForm):

    class Meta:
        model = Topic
        fields = ('title', 'description')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 16}),
        }
