from django.conf import settings

import allauth.socialaccount.providers

import allauth.socialaccount.providers.openid.forms as openid_forms
import allauth.socialaccount.providers.openid.views as openid_views


def get_openid_brands(request):
    brands = {}
    provider = allauth.socialaccount.providers.registry.by_id('openid')
    for brand in provider.get_brands():
        brands['openid.%s' % brand['id']] = {
            'id': brand['id'],
            'name': brand['name'],
            'url': provider.get_login_url(request, openid=brand['openid_url']),
        }
    return brands


def get_other_providers(request, exclude):
    providers = {}
    for provider in allauth.socialaccount.providers.registry.get_list():
        if provider.id in exclude:
            continue
        providers[provider.id] = {
            'id': provider.id,
            'name': provider.name,
            'url': provider.get_login_url(request),
        }
    return providers


def get_auth_providers(request):
    providers = get_openid_brands(request)
    providers.update(get_other_providers(request, exclude={'openid'}))
    for name, logo in settings.SORTED_AUTH_PROVIDERS:
        yield dict(providers[name], logo=logo)


def get_openid_providers(request):
    providers = []
    openid_form = None
    for provider in settings.SORTED_OPENID_PROVIDERS:
        errors = []

        if request.method == 'POST' and request.POST.get('login') == provider['name']:
            if provider['pattern'] and request.POST.get('openid', ''):
                data = request.POST.copy()
                data['openid'] = provider['pattern'] % data['openid']
            else:
                data = request.POST
            form = openid_forms.LoginForm(data)
            if form.is_valid():
                openid_form = form
            else:
                errors.extend([error for error in form.non_field_errors()])
                errors.extend([error for error in form['openid'].errors])
        else:
            form = openid_forms.LoginForm()

        providers.append({
            'form': form,
            'name': provider['name'],
            'url': provider['url'],
            'errors': errors,
        })

    return providers, openid_form


def openid_login(request, form):
    request.POST = request.POST.copy()
    request.POST['openid'] = form.data['openid']
    request.REQUEST.dicts = ({'openid': form.data['openid']},) + request.REQUEST.dicts
    return openid_views.login(request)
