import io
import json
import base64
import pathlib
import unidecode
import collections
import datetime

from django.core.management.base import BaseCommand
from django.core.files import File

from manopozicija import models
from manopozicija import helpers


def clean_name(name):
    name = ' '.join(name.strip().split())
    return unidecode.unidecode(name).lower()


class Command(BaseCommand):
    """

    .ndjson file should contain these fields:

        {
            'fname': <first name>,
            'lname': <last name>,
            'bdate': <birth date>,
            'partial': <bool: true if data does not cover all terms>,
            'photo': {
                'type': <photo file extension>,
                'data': <base64 encoded photo>,
            }
            'terms': [
                {
                    'body': <body>,
                    'since': <date>,
                    'until': <date>,
                    'party': <party>,
                    'elected': <bool: elected or not>,
                }
            ]
        }

    """

    help = 'Import photos from ndjson file.'

    def add_arguments(self, parser):
        parser.add_argument('path', help="Path to the NDJSON file containing photos")

    def handle(self, path, **options):
        printer = helpers.Printer(self.stdout, options['verbosity'])
        path = pathlib.Path(path)

        # ------------------------------------------

        # 'fname': <first name>,
        # 'lname': <last name>,
        # 'bdate': <birth date>,
        # 'title': <title or profession>,
        # 'partial': <bool: true if data covers only one or few elections, but not all of them>,
        # 'elections': [
        #     {
        #         'body': <body, for example 'Seimas'>,
        #         'since': <date, when elections started>,
        #         'until': <date, until next elections>,
        #         'party': <party>,
        #         'photo': {
        #             'ext': <photo file extension>,
        #             'data': <base64 encoded photo file>,
        #         },
        #         'elected': <bool: elected or not>,
        #     }
        # ]

        now = datetime.datetime.now()
        strptime = datetime.datetime.strptime

        Photo = collections.namedtuple('Photo', 'type, data')
        Election = collections.namedtuple('Term', 'body, since, until, party, photo, elected')
        Candidate = collections.namedtuple('Candidate', 'fname, lname, bdate, partial, elections')

        with path.open(encoding='utf-8') as f:
            for line in f:
                row = json.loads(line)
                row['elections'] = [
                    Election(**dict(
                        x,
                        since=strptime(x['since'], '%Y-%m-%d'),
                        until=strptime(x['until'], '%Y-%m-%d'),
                        photo=Photo(**x['photo']),
                    )) for x in row['elections']
                ]
                candidate = Candidate(**dict(
                    row,
                    bdate=strptime(row['bdate']),
                ))

                # Update candidate
                printer.info('')
                printer.info('{bdate} {fname} {lname}'.format(**row))
                actor, created = models.Actor.objects.get_or_create(
                    birth_date=candidate.bdate,
                    first_name=candidate.fname,
                    last_name=candidate.lname,
                    defaults={
                        'title': candidate.title,
                    },
                )

                # Update candidate photo
                if not actor.photo and candidate.elections:
                    photo = candidate.elections[-1].photo
                    filename = '%s-%s.%s' % (candidate.fname, candidate.lname, photo.ext)
                    content = io.BytesIO(base64.b64decode(photo.data.encode('ascii')))
                    actor.photo.save(filename, File(content), save=True)

                actor_groups = actor.ingroups.values_list('pk', flat=True)
                actor_parties = {x.pk: x for x in models.Member.objects.filter(actor=actor)}
                for election in candidate.elections:
                    # Get election body (must be created manually)
                    body = models.Body.objects.get(name=election.body)

                    # Get or create election term
                    term, created = models.Term.objects.get_or_create(
                        body=body,
                        title='%d-%d metų kadencija' % (
                            election.since.year,
                            election.until.year if election.until else now.year,
                        )
                    )

                    # Get or create group for this election
                    group_title = {
                        'Seimas': 'Seimą',
                    }
                    group, created = models.Group.objects.get_or_create(
                        title='Kandidatai į %d metų %s' % (
                            election.since.year,
                            group_title[election.body],
                        ),
                        defaults={
                            'timestamp': election.since,
                        },
                    )

                    # Add current candidate to the election group
                    if group.pk not in actor_groups:
                        group.members.add(actor)

                    # Get or create party
                    party, created = models.Actor.objects.get_or_create(
                        first_name=election.party,
                        group=True,
                        defaults={
                            'body': body,
                            'title': 'plitinė partija',
                        },
                    )

                    # Update party membership information
                    membership = actor_parties.get(party.pk, None)
                    if membership is None:
                        models.Member.objects.get_or_create(actor=actor, group=party, defaults={
                            'since': election.since,
                            'until': election.until,
                        })
                    elif (
                        (election.since and membership.since.date() != election.since.date()) or
                        (election.until and membership.until.date() != election.until.date())
                    ):
                        if election.since:
                            membership.since = min(membership.since, election.since)
                        if election.until:
                            membership.until = max(membership.until, election.until)
                        membership.save()

            printer.info('done.')
