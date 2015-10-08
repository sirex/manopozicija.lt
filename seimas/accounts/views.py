from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import auth
from django.utils.translation import ugettext
from django.contrib import messages
from django.contrib.auth.decorators import login_required

import seimas.accounts.helpers.allauth as allauth_helpers
import seimas.accounts.forms as accounts_forms
from seimas.website.helpers import formrenderer


def login(request):
    openid_providers, form = allauth_helpers.get_openid_providers(request)
    if form:
        return allauth_helpers.openid_login(request, form)
    else:
        return render(request, 'accounts/login.html', {
            'auth_providers': allauth_helpers.get_auth_providers(request),
            'openid_providers': openid_providers,
        })


def logout(request):
    auth.logout(request)
    return redirect('topic-list')


@login_required
def settings(request):
    if request.method == 'POST':
        form = accounts_forms.SettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, ugettext("Nustatymai buvo sėkimingai išsaugoti."))
            return redirect('accounts_settings')
    else:
        form = accounts_forms.SettingsForm(instance=request.user)
    return render(request, 'accounts/settings.html', {
        'form': formrenderer.render(request, form, title=ugettext("Profilio nustatymai"), submit=ugettext("Saugoti")),
    })
