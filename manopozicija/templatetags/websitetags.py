import yattag
import markdown

from django import template
from django.contrib import messages
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(name='messages', takes_context=True)
def messages_tag(context):
    level_mappig = {
        messages.SUCCESS: 'success',
        messages.INFO: 'info',
        messages.WARNING: 'warning',
        messages.ERROR: 'danger',
    }

    doc, tag, text = yattag.Doc().tagtext()
    for message in messages.get_messages(context['request']):
        level = level_mappig.get(message.level, 'info')
        with tag('div', klass='alert alert-%s' % level, role='alert'):
            text(str(message))
    return mark_safe(doc.getvalue())


@register.filter(name='markdown')
def markdown_tag(value):
    return mark_safe(markdown.markdown(value, extensions=['markdown.extensions.attr_list']))
