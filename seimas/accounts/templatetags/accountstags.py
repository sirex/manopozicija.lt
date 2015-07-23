from django import template
from django.core.exceptions import ImproperlyConfigured

from allauth.socialaccount import providers

register = template.Library()


@register.simple_tag()
def username(user):
    if user.first_name or user.last_name:
        return user.get_full_name()
    elif user.username and user.username != 'user':
        return user.username
    elif user.email and '@' in user.email:
        return user.email.split('@')[0]
    else:
        return 'User #%d' % user.pk


@register.simple_tag(takes_context=True)
def providers_media_js(context):
    result = []
    request = context['request']
    for p in providers.registry.get_list():
        try:
            result.append(p.media_js(request))
        except ImproperlyConfigured:
            pass
    return '\n'.join(result)
