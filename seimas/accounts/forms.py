from django import forms
from django.utils.translation import ugettext_lazy as _
import django.contrib.auth.models as auth_models


class SettingsForm(forms.ModelForm):
    class Meta:
        model = auth_models.User
        fields = ('first_name', 'last_name', 'email')
        help_texts = {
            'email': _(
                "Bus naudojamas komunikacijai. Jei pageidaujate negauti jokių laiškų, palikite šį lauką tuščią."
            ),
        }
