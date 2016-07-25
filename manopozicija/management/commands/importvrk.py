import csv
import pathlib
import datetime
import itertools
import collections

from django.core.management.base import BaseCommand

from manopozicija import models
from manopozicija import helpers


def import_terms(reader, typemap):
    for row in reader:
        {
            'PRADZIA': '2016-11-17',
            'PABAIGA': '',
            'PAVADINIMAS': '2016-2020 metų kadencija',
            'KADENCIJOS_ID': '664',
            'RUSIS': 'SEI',
            'EILES_NUMERIS': '8'
        }
        if row['RUSIS'] == 'SEI':
            models.Term.objects.update_or_create(
                source=models.Term.VRK_KADENCIJOS_CSV, source_id=row['KADENCIJOS_ID'], defaults={
                    'body': typemap[row['RUSIS']],
                    'since': datetime.datetime.strptime(row['PRADZIA'], '%Y-%m-%d'),
                    'until': datetime.datetime.strptime(row['PABAIGA'], '%Y-%m-%d') if row['PABAIGA'] else None,
                    'title': row['PAVADINIMAS'],
                }
            )


class Command(BaseCommand):
    help = 'Imports posts to an existing topic'

    def add_arguments(self, parser):
        parser.add_argument('path', help="Path to directory with CSV files")

    def handle(self, path, **options):
        path = pathlib.Path(path)
        printer = helpers.Printer(self.stdout, options['verbosity'])

        seimas, created = models.Body.objects.get_or_create(name='Seimas')

        typemap = {
            'SEI': seimas,
        }

        printer.info('Importing terms...')
        with (path / 'kadencijos.csv').open() as f:
            reader = csv.DictReader(f)
            import_terms(reader, typemap)

        printer.info('Importing candidates and parties...')
        with (path / 'kadencijos.csv').open() as f:
            Term = collections.namedtuple('Term', 'id body since until')
            terms = {
                row['KADENCIJOS_ID']: Term(
                    id=row['KADENCIJOS_ID'],
                    body=typemap[row['RUSIS']],
                    since=datetime.datetime.strptime(row['PRADZIA'], '%Y-%m-%d'),
                    until=datetime.datetime.strptime(row['PABAIGA'], '%Y-%m-%d') if row['PABAIGA'] else None,
                )
                for row in csv.DictReader(f) if row['RUSIS'] == 'SEI'
            }

        with (path / 'rinkimai.csv').open() as f:
            Election = collections.namedtuple('Election', 'term date')
            elections = {
                row['VYKDOMU_RINKIMU_TURO_ID']: Election(
                    term=terms[row['KADENCIJOS_ID']],
                    date=datetime.datetime.strptime(row['RINKIMU_TURO_DATA'], '%Y-%m-%d'),
                )
                for row in csv.DictReader(f) if row['KADENCIJOS_ID'] in terms
            }

        with (path / 'organizacijos.csv').open() as f:
            organisations = {
                row['ORGANIZACIJOS_ID']: row['ORGANIZACIJOS_PAVADINIMAS']
                for row in csv.DictReader(f)
            }

        def name(name):
            return ' '.join([x.title() for x in name.split()])

        with (path / 'kandidatai.csv').open() as f:
            Candidate = collections.namedtuple('Candidate', 'birth_date last_name first_name')
            CandidateElection = collections.namedtuple('CandidateElection', 'elected election vienmandate daugiamandate')
            candidates = collections.defaultdict(list)
            for row in csv.DictReader(f):
                if row['VR_TURO_ID'] in elections:
                    candidate = Candidate(row['GIMIMO_DATA'], name(row['PAVARDE']), name(row['VARDAS']))
                    vienmandate = row['VIENMANDATE_ORGANIZACIJA']
                    daugiamandate = row['DAUGIAMANDATE_ORGANIZACIJA']
                    candidates[candidate].append(CandidateElection(
                        elected=row['AR_ISRINKTAS'] == 'T',
                        election=elections[row['VR_TURO_ID']],
                        vienmandate=organisations[vienmandate] if vienmandate else None,
                        daugiamandate=organisations[daugiamandate] if daugiamandate else None,
                    ))

        for candidate, rounds in candidates.items():
            printer.info('')
            printer.info('%s %s %s' % candidate)

            membership = {}
            rounds = sorted(rounds, key=lambda x: x.election.term.since)
            rounds_by_term = itertools.groupby(rounds, key=lambda x: x.election.term.id)

            times_elected = sum(1 for x in rounds if x.elected)
            times_candidate = 0

            for term_id, term_rounds in rounds_by_term:
                times_candidate += 1
                term_rounds = list(term_rounds)
                term = terms[term_id]
                elected = sorted([x.election.date for x in term_rounds if x.elected])
                result = ('elected: %s' % elected[0].strftime('%Y-%m-%d')) if elected else ''
                printer.info('  %s-%s %s' % (
                    term.since.strftime('%Y'),
                    term.until.strftime('%Y') if term.until else '    ',
                    result,
                ))

                orgs = set()
                orgs.update(x.vienmandate for x in term_rounds if x.vienmandate)
                orgs.update(x.daugiamandate for x in term_rounds if x.daugiamandate)

                if orgs:
                    for org in sorted(orgs):
                        printer.info('    %s' % org)
                        since, until = membership.get(org, (min(elected, default=term.since), term.until))
                        membership[org] = (
                            min(since, term.since),
                            max(until, term.until) if until and term.until else term.until,
                        )

            printer.info('  Member of:')
            for org, (since, until) in membership.items():
                printer.info('    %s (%s - %s)' % (
                    org,
                    since.strftime('%Y-%m-%d'),
                    until.strftime('%Y-%m-%d') if until else '',
                ))

            actor_title = 'seimo narys' if times_elected > 0 else ''

            actor, created = models.Actor.objects.get_or_create(
                birth_date=candidate.birth_date,
                first_name=candidate.first_name,
                last_name=candidate.last_name,
                defaults={
                    'title': actor_title,
                    'times_elected': times_elected,
                    'times_candidate': times_candidate,
                },
            )

            if not created:
                modified = [
                    actor.times_elected != times_elected,
                    actor.times_candidate != times_candidate,
                ]
                if any(modified):
                    actor.times_elected = times_elected
                    actor.times_candidate = times_candidate
                    actor.save()

            for org, (since, until) in membership.items():
                party, created = models.Actor.objects.get_or_create(first_name=org, group=True, defaults={
                    'title': 'plitinė partija',
                    'body': seimas,
                })

                models.Member.objects.get_or_create(actor=actor, group=party, defaults={
                    'since': since,
                    'until': until,
                })

        printer.info('done.')
