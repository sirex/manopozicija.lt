import logging

from django.http import JsonResponse, Http404
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory, modelformset_factory
from django.contrib.contenttypes.models import ContentType

from manopozicija import models
from manopozicija import services
from manopozicija import forms
from manopozicija import helpers
from manopozicija.indicators import get_indicator_data

logger = logging.getLogger(__name__)


def topic_list(request):
    return render(request, 'index.html', {
        'group': models.Group.objects.order_by('-timestamp').first(),
        'topics': helpers.get_topics(),
    })


def topic_details(request, object_id, slug):
    topic = get_object_or_404(models.Topic, pk=object_id)
    is_topic_curator = services.is_topic_curator(request.user, topic)
    return render(request, 'manopozicija/topic_details.html', {
        'topic': topic,
        'arguments': helpers.get_arguments(services.get_topic_arguments(topic)),
        'posts': helpers.get_posts(request.user, topic, services.get_topic_posts(topic)),
        'queue': (
            helpers.get_posts(request.user, topic, services.get_topic_posts(topic, queue=True))
            if is_topic_curator else []
        ),
        'has_indicators': topic.indicators.count() > 0,
        'indicators': helpers.get_indicators(topic),
        'is_topic_curator': is_topic_curator,
        'curators': helpers.get_topic_curators(topic) if is_topic_curator else []
    })


def topic_kpi(request, object_id, slug):
    topic = get_object_or_404(models.Topic, pk=object_id)
    event_type = ContentType.objects.get(app_label='manopozicija', model='event')
    return JsonResponse({
        'indicators': [
            {
                'id': x.pk,
                'ylabel': x.ylabel,
                'data': get_indicator_data(x),
            }
            for x in topic.indicators.all()
        ],
        'events': [
            {
                'id': x.pk,
                'title': x.content_object.title,
                'date': x.timestamp.strftime('%Y-%m-%d'),
                'source': x.content_object.source_link,
                'position': x.position,
            }
            for x in (
                models.Post.objects.
                filter(topic=topic, content_type=event_type, approved__isnull=False).
                order_by('timestamp')
            )
        ],
    })


@login_required
def quote_form(request, object_id, slug):
    topic = get_object_or_404(models.Topic, pk=object_id)
    ArgumentFormSet = formset_factory(
        forms.ArgumentForm, min_num=0, max_num=3, extra=3,
        validate_min=True, validate_max=True,
    )

    if request.method == 'POST':
        source_form = forms.SourceForm(request.POST)
        source_form.full_clean()
        source = source_form.cleaned_data
        form = forms.CombinedForms(
            source=source_form,
            quote=forms.QuoteForm(topic, source.get('actor'), source.get('source_link'), request.POST),
            arguments=ArgumentFormSet(request.POST),
        )
        if form.is_valid():
            services.create_quote(request.user, topic, **form.cleaned_data)
            return redirect(topic)
    else:
        form = forms.CombinedForms(
            source=forms.SourceForm(),
            quote=forms.QuoteForm(topic, actor=None, source_link=None),
            arguments=ArgumentFormSet(),
        )

    return render(request, 'manopozicija/quote_form.html', {
        'topic': topic,
        'source_form': form['source'],
        'quote_form': form['quote'],
        'arguments_formset': form['arguments'],
    })


@login_required
def quote_update_form(request, object_id):
    post = get_object_or_404(models.Post, pk=object_id)
    quote = get_object_or_404(models.Quote, post=post)
    source = quote.source
    topic = post.topic
    is_topic_curator = services.is_topic_curator(request.user, topic)

    if not is_topic_curator:
        raise Http404('User is not a topic curator.')

    arguments = models.PostArgument.objects.filter(post=post)
    ArgumentFormSet = modelformset_factory(
        models.PostArgument, form=forms.ArgumentForm,
        min_num=0, max_num=3, extra=3, validate_min=True, validate_max=True,
    )

    if request.method == 'POST':
        source_form = forms.SourceForm(request.POST, instance=source)
        source_form.full_clean()
        source = source_form.cleaned_data
        form = forms.CombinedForms(
            source=source_form,
            quote=forms.QuoteForm(topic, source.get('actor'), source.get('source_link'), request.POST, instance=quote),
            arguments=ArgumentFormSet(request.POST, queryset=arguments),
        )
        if form.is_valid():
            services.update_quote(request.user, topic, post, quote, arguments, form.cleaned_data)
            return redirect(topic)
    else:
        form = forms.CombinedForms(
            source=forms.SourceForm(instance=source),
            quote=forms.QuoteForm(topic, actor=None, source_link=None, instance=quote),
            arguments=ArgumentFormSet(queryset=arguments),
        )

    return render(request, 'manopozicija/quote_form.html', {
        'topic': topic,
        'source_form': form['source'],
        'quote_form': form['quote'],
        'arguments_formset': form['arguments'],
    })


@login_required
def post_delete(request, object_id):
    post = get_object_or_404(models.Post, pk=object_id)
    is_topic_curator = services.is_topic_curator(request.user, post.topic)
    if not is_topic_curator:
        raise Http404('User is not a topic curator.')
    services.delete_post(post)
    return redirect(post.topic)


@login_required
def event_form(request, object_id, slug):
    topic = get_object_or_404(models.Topic, pk=object_id)
    if request.method == 'POST':
        form = forms.EventForm(topic, request.POST)
        if form.is_valid():
            services.create_event(request.user, topic, form.cleaned_data)
            return redirect(topic)
    else:
        form = forms.EventForm(topic)
    return render(request, 'manopozicija/form.html', {
        'form_name': 'event-form',
        'form_title': ugettext('Naujas įvykis'),
        'forms': [form],
    })


@login_required
def person_form(request):
    if request.method == 'POST':
        form = forms.PersonForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = forms.PersonForm()
    return render(request, 'manopozicija/form.html', {
        'form_name': 'person-form',
        'form_title': ugettext('Naujas asmuo'),
        'forms': [form],
    })


@login_required
def group_form(request):
    if request.method == 'POST':
        form = forms.GroupForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = forms.GroupForm()
    return render(request, 'manopozicija/form.html', {
        'form_name': 'group-form',
        'form_title': ugettext('Nauja grupė'),
        'forms': [form],
    })


@login_required
def curator_form(request, object_id, slug):
    user = request.user
    full_name = ' '.join([user.first_name, user.last_name]).strip()
    topic = get_object_or_404(models.Topic, pk=object_id)
    if request.method == 'POST':
        form = forms.CombinedForms(
            user_data=None if full_name else forms.CuratorUserForm(request.POST),
            curator=forms.CuratorForm(request.POST, request.FILES),
        )
        if form.is_valid():
            services.create_curator(user, topic, **form.cleaned_data)
            return redirect(topic)
    else:
        form = forms.CombinedForms(
            user_data=None if full_name else forms.CuratorUserForm(),
            curator=forms.CuratorForm(),
        )
    return render(request, 'manopozicija/form.html', {
        'page_title': str(topic),
        'form_name': 'curator-form',
        'form_title': ugettext('Tapk temos kuratoriumi'),
        'forms': form.forms,
    })


@login_required
def curator_post_vote(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(models.Post, pk=post_id)
        form = forms.VoteForm(request.POST)
        if form.is_valid():
            if services.is_topic_curator(request.user, post.topic):
                curator_type = ContentType.objects.get(app_label='manopozicija', model='curator')
                voted_for_himself = (
                    post.content_type == curator_type and
                    request.user == post.content_object.user and
                    not request.user.is_superuser
                )
                if voted_for_himself:
                    logger.debug((
                        '%r user voted for his own curator application on %r topic for %r post with vote: %r'
                    ), request.user, post.topic, post, form.cleaned_data['vote'])
                else:
                    upvotes, downvotes = services.update_curator_position(request.user, post, form.cleaned_data['vote'])
                    return JsonResponse({'success': True, 'upvotes': upvotes, 'downvotes': downvotes})
            else:
                logger.debug((
                    '%r user who is not a %r topic curator attempted to vote for %r post with vote: %r'
                ), request.user, post.topic, post, form.cleaned_data['vote'])
        else:
            logger.debug('form error: %s', form.errors.as_text())
    else:
        logger.debug('only POST is allowed, got %s instead', request.method)
    return JsonResponse({'success': False})


@login_required
def user_post_vote(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(models.Post, pk=post_id)
        form = forms.VoteForm(request.POST)
        if form.is_valid():
            upvotes, downvotes = services.update_user_position(request.user, post, form.cleaned_data['vote'])
            return JsonResponse({'success': True, 'upvotes': upvotes, 'downvotes': downvotes})
        else:
            logger.debug('form error: %s', form.errors.as_text())
    else:
        logger.debug('only POST is allowed, got %s instead', request.method)
    return JsonResponse({'success': False})


@login_required
def compare_positions(request, object_id, slug):
    group = get_object_or_404(models.Group, pk=object_id)
    return render(request, 'manopozicija/compare_positions.html', {
        'group': group,
        'positions': helpers.get_positions(group, request.user),
    })
