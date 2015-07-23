from seimas.website.models import Voting
from seimas.website.models import Vote


def update_voting(voting: Voting, data: dict):
    """Update voting from data returned by seimas.website.parsers.parse_votes."""
    voting.datetime = data['datetime']
    voting.vid = data['id']
    voting.question = data['question']
    voting.result = data['result']
    voting.sitting_no = str(data['sitting_no'])
    voting.link = data['url']


def import_votes(voting: Voting, votes: list):
    """Import votes from data returned by seimas.website.parsers.parse_votes."""
    voting.vote_set.all().delete()

    position_map = {
        'aye': Vote.AYE,
        'no': Vote.NO,
        'abstain': Vote.ABSTAIN,
        'no-vote': Vote.NO_VOTE,
    }

    for vote in votes:
        Vote.objects.create(
            voting=voting,
            name=vote['name'],
            link=vote['link'],
            fraction=vote['fraction'],
            position=position_map[vote['position']],
        )
