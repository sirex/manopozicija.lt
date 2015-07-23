import yattag
import markdown

import django.forms
from django.middleware import csrf
from django.utils.translation import ugettext


class Bootstrap3(object):
    def __init__(self, request, form, title=None, submit=ugettext('Submit'), description=''):
        self.request = request
        self.form = form
        self.title = title
        self.submit = submit
        self.description = description
        self.doc, self.tag, self.text = yattag.Doc().tagtext()

    def csrf_token(self):
        csrf_token = csrf.get_token(self.request)
        if csrf_token and csrf_token != 'NOTPROVIDED':
            self.doc.stag('input', type='hidden', name='csrfmiddlewaretoken', value=csrf_token)

    def markdown(self, text: str):
        self.doc.asis(markdown.markdown(text, extensions=['markdown.extensions.attr_list']))

    def errors(self, errors):
        if errors:
            with self.tag('div', klass='help-block'):
                for error in errors:
                    with self.tag('p', klass='text-danger'):
                        self.markdown(str(error))

    def help_text(self, field):
        with self.tag('div', klass='help-block'):
            self.markdown(str(field.help_text))

    def label(self, field):
        suffix = '*' if field.field.required else ''
        self.doc.asis(field.label_tag(label_suffix=suffix, attrs={'class': 'col-sm-2 control-label'}))

    def field(self, field: django.forms.Field):
        classes = ' has-error' if field.errors else ''
        with self.tag('div', klass='form-group' + classes):
            self.label(field)
            with self.tag('div', klass='col-sm-10'):
                self.doc.asis(field.as_widget(attrs={'class': 'form-control'}))
                self.errors(field.errors)
                if field.help_text:
                    self.help_text(field)

    def buttons(self):
        with self.tag('div', klass='form-group'):
            with self.tag('div', klass='col-sm-offset-2 col-sm-10'):
                with self.tag('button', type='submit', klass='btn btn-primary'):
                    self.text(self.submit)

    def fields(self):
        self.errors(self.form.non_field_errors())
        for field in self.form:
            self.field(field)

    def render(self):
        with self.tag('form', klass='form-horizontal', method='post'):
            if self.title:
                with self.tag('div', klass='col-sm-offset-2 col-sm-10'):
                    with self.tag('h1'):
                        self.text(str(self.title))
            if self.description:
                with self.tag('div', klass='col-sm-offset-2 col-sm-10 alert alert-info', role='alert'):
                    # with self.tag('div', klass='alert alert-info', role='alert'):
                    self.markdown(str(self.description))
            self.csrf_token()
            self.fields()
            self.buttons()
        return self.doc.getvalue()


def render(request, form: django.forms.Form, **kwargs):
    return Bootstrap3(request, form, **kwargs).render()


def render_fields(request, form: django.forms.Form):
    renderer = Bootstrap3(request, form)
    renderer.fields()
    return renderer.doc.getvalue()
