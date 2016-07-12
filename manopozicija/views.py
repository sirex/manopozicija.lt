import requests

from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory

from manopozicija.indicators import get_indicator_data
from manopozicija import models
from manopozicija import services
from manopozicija import forms


def topic_list(request):
    return render(request, 'index.html', {
        'topics': models.Topic.objects.order_by('-created'),
    })


def topic_details(request, object_id, slug):
    topic = get_object_or_404(models.Topic, pk=object_id)

    return render(request, 'manopozicija/topic_details.html', {
        'topic': topic,
        'posts': services.get_topic_posts(topic),
        'has_indicators': topic.indicators.count() > 0,
    })


def topic_kpi(request, slug):
    topic = get_object_or_404(Topic, slug=slug)
    return JsonResponse({
        'indicators': [
            {
                'title': x.title,
                'source': x.source,
                'ylabel': x.ylabel,
                'data': get_indicator_data(x),
            }
            for x in topic.indicators.all()
        ],
        'events': [
            {
                'title': x.title,
                'date': x.datetime.strftime('%Y-%m-%d'),
                'source': x.link,
                'position': None,  # TODO: Currently position is stored for each voting by person and here we need
                                   #       aggregated mean of all positions for this one voting.
            }
            for x in Voting.objects.filter(position__topic=topic).order_by('datetime')
        ],
    })


@login_required
def voting_form(request, slug):
    topic = get_object_or_404(Topic, slug=slug)

    if request.method == 'POST':
        form = NewVotingForm(topic, request.POST)
        if form.is_valid():
            voting = form.save(commit=False)
            voting.author = request.user

            resp = requests.get(voting.link)
            data = parse_votes(voting.link, resp.content)
            update_voting(voting, data)

            voting.save()

            weight = form.cleaned_data['weight']

            Position.objects.create(topic=topic, content_object=voting, weight=weight)

            import_votes(voting, data['table'])
            create_vote_positions(topic, voting, weight)

            messages.success(request, ugettext("Voting „%s“ created." % voting))
            return redirect(topic)
    else:
        form = NewVotingForm(topic)

    return render(request, 'website/voting_form.html', {
        'topic': topic,
        'form': formrenderer.render(request, form, title=ugettext('Naujas balsavimas'), submit=ugettext('Pridėti')),
    })


@login_required
def news_form(request, slug):
    topic = get_object_or_404(Topic, slug=slug)

    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            news = form.save(commit=False)

            weight = form.cleaned_data['weight']
            Position.objects.create(topic=topic, content_object=news, weight=weight)

            messages.success(request, ugettext("News „%s“ created." % news))
            return redirect(topic)
    else:
        form = QuoteForm()

    return render(request, 'website/news_form.html', {
        'form': formrenderer.render(request, form, title=ugettext('Nauja naujiena'), submit=ugettext('Pridėti')),
    })


@login_required
def topic_form(request):
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.author = request.user
            topic.save()
            messages.success(request, ugettext("Topic „%s“ created." % topic))
            return redirect(topic)
    else:
        form = TopicForm()

    return render(request, 'website/topic_form.html', {
        'form': formrenderer.render(request, form, title=ugettext('Nauja tema'), submit=ugettext('Pridėti')),
    })


@login_required
def quote_form(request, object_id, slug):
    topic = get_object_or_404(models.Topic, pk=object_id)
    ArgumentFormSet = formset_factory(
        forms.ArgumentForm, min_num=1, max_num=3, extra=3,
        validate_min=True, validate_max=True,
    )

    if request.method == 'POST':
        source_form = forms.SourceForm(request.POST)
        quote_form = forms.QuoteForm(request.POST)
        arguments_formset = ArgumentFormSet(request.POST)
        if all([source_form.is_valid(), quote_form.is_valid(), arguments_formset.is_valid()]):
            services.add_new_quote(
                request.user, topic,
                source_form.cleaned_data,
                quote_form.cleaned_data,
                arguments_formset.cleaned_data,
            )
            return redirect(topic)
    else:
        source_form = forms.SourceForm()
        quote_form = forms.QuoteForm()
        arguments_formset = ArgumentFormSet()

    return render(request, 'manopozicija/quote_form.html', {
        'topic': topic,
        'source_form': source_form,
        'quote_form': quote_form,
        'arguments_formset': arguments_formset,
    })


@login_required
def person_form(request):
    if request.method == 'POST':
        form = forms.PersonForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = forms.PersonForm()
    return render(request, 'manopozicija/form.html', {
        'form_name': 'person-form',
        'form_title': ugettext('Naujas asmuo'),
        'form': form,
    })
