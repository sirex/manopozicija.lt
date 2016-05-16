import yaml
import os.path

from django.http import Http404
from django.conf.urls import url
from django.conf import settings


def get_page(path):
    url = ('/%s/' % path) if path else '/'
    with (settings.PROJECT_DIR / 'prototype.yml').open(encoding='utf-8') as f:
        data = yaml.load(f)
    try:
        page = data['urls'][url] or {
            'context': {},
        }
    except KeyError:
        raise Http404("Requested %s page not found." % url)

    if 'globals' in data and page.get('type', 'html') == 'html':
        page['context'] = dict(data['globals'], **page.get('context', {}))

    return page


def get_template(path):
    base = settings.PROJECT_DIR / 'seimas/website'
    candidates = [
        os.path.join(path, 'index.html'),
        '%s.html' % path,
    ]
    for template in candidates:
        if (base / 'templates' / template).exists():
            return template


def get_urls(view):
    with (settings.PROJECT_DIR / 'prototype.yml').open(encoding='utf-8') as f:
        data = yaml.load(f)

    urls = []
    for path, page in data['urls'].items():
        if page and 'name' in page:
            pattern = r'^%s$' % path.lstrip('/')
            kwargs = {'path': path.strip('/')}
            urls.append(url(pattern, view, kwargs, name=page['name']))
    return urls
