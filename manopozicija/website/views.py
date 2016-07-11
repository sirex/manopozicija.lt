import requests

from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth.decorators import login_required

from manopozicija.website.helpers import formrenderer
# from manopozicija.website.forms import NewVotingForm, TopicForm, QuoteForm
# from manopozicija.models import Topic
# from manopozicija.models import Position
# from manopozicija.models import Voting
from manopozicija.website.parsers.votings import parse_votes
from manopozicija.website.services.voting import update_voting, import_votes, create_vote_positions
from manopozicija.website.helpers.decorators import superuser_required
from manopozicija.indicators import get_indicator_data


def topic_list(request):
    return render(request, 'index.html', {
        'topics': Topic.objects.order_by('-modified'),
    })


def topic_details(request, slug):
    topic = get_object_or_404(Topic, slug=slug)
    votings = Voting.objects.filter(position__topic=topic).order_by('-datetime')

    people = (
        Position.objects.values('person__name').
        filter(topic=topic, person__isnull=False).
        annotate(weight=Sum('weight'))
    )
    supporters = people.filter(weight__gt=0).order_by('-weight')
    critics = people.filter(weight__lt=0).order_by('weight')

    return render(request, 'website/topic_details.html', {
        'topic': topic,
        'votings': votings,
        'supporters': list(supporters[:10]),
        'supporters_count': supporters.count(),
        'critics': list(critics[:10]),
        'critics_count': critics.count(),
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


@superuser_required
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


@superuser_required
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
