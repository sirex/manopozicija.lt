from django.http import JsonResponse
from django.shortcuts import render

from seimas.prototype.helpers import get_page
from seimas.prototype.helpers import get_template


def prototype(request, path):
    page = get_page(path)
    context = page['context']
    if page.get('type') == 'json':
        return JsonResponse(context)
    else:
        return render(request, get_template(path), context)
