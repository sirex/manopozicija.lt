# from manopozicija.models import Voting
# from manopozicija.models import Vote
from manopozicija.models import Actor
from manopozicija.models import Timeline


def update_voting(voting, data: dict):
    """Update voting from data returned by manopozicija.website.parsers.parse_votes."""
    voting.datetime = data['datetime']
    voting.vid = data['id']
    voting.question = data['question']
    voting.question_a = data['question_a']
    voting.question_b = data['question_b']
    voting.result = data['result']
    voting.sitting_no = str(data['sitting_no'])
    voting.link = data['url']


def import_votes(voting, votes: list):
    """Import votes from data returned by manopozicija.website.parsers.parse_votes."""
    voting.vote_set.all().delete()

    position_map = {
        'aye': Vote.AYE,
        'no': Vote.NO,
        'abstain': Vote.ABSTAIN,
        'no-vote': Vote.NO_VOTE,
    }

    for vote in votes:
        person = get_or_create_person_by_name(vote['name'])

        Vote.objects.create(
            voting=voting,
            person=person,
            name=vote['name'],
            link=vote['link'],
            fraction=vote['fraction'],
            vote=position_map[vote['position']],
        )


def get_or_create_person_by_name(name):
    try:
        return Person.objects.get(name__iexact=name)
    except Person.DoesNotExist:
        return Person.objects.create(name=name)


def create_vote_positions(topic, voting, weight):
    for vote in voting.vote_set.order_by('pk'):
        Position.objects.create(topic=topic, person=vote.person, content_object=vote, weight=vote.score * weight)
