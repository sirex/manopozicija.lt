import datetime
import pytest
import pkg_resources as pres

from seimas import indicators
from seimas.website.models import Indicator

dt = datetime.datetime


def tuples(frame):
    return list(map(tuple, frame.to_records()))


@pytest.mark.django_db
def test_import_indicators():
    assert Indicator.objects.count() == 0

    def get_indicators():
        return [(x.slug, x.deleted is not None) for x in Indicator.objects.all()]

    # Initial import to an empty table
    indicators.import_indicators([
        ('a', {'fetch': 'a', 'title': 'A', 'ylabel': 'A'}),
        ('b', {'fetch': 'b', 'title': 'B', 'ylabel': 'B'}),
    ])
    assert get_indicators() == [('a', False), ('b', False)]

    # Add new indicator
    indicators.import_indicators([
        ('a', {'fetch': 'a', 'title': 'A', 'ylabel': 'A'}),
        ('b', {'fetch': 'b', 'title': 'B', 'ylabel': 'B'}),
        ('c', {'fetch': 'c', 'title': 'C', 'ylabel': 'C'}),
    ])
    assert get_indicators() == [('a', False), ('b', False), ('c', False)]

    # Remove an existing indicator
    indicators.import_indicators([
        ('a', {'fetch': 'a', 'title': 'A', 'ylabel': 'A'}),
        ('b', {'fetch': 'b', 'title': 'B', 'ylabel': 'B'}),
    ])
    assert get_indicators() == [('a', False), ('b', False), ('c', True)]

    # Add an removed indicator again
    indicators.import_indicators([
        ('a', {'fetch': 'a', 'title': 'A', 'ylabel': 'A'}),
        ('b', {'fetch': 'b', 'title': 'B', 'ylabel': 'B'}),
        ('c', {'fetch': 'c', 'title': 'C', 'ylabel': 'C'}),
    ])
    assert get_indicators() == [('a', False), ('b', False), ('c', False)]


def test_voter_turnout():
    path = pres.resource_filename('seimas.website.tests', 'fixtures/indicators/voter_turnout.tsv.gz')
    frame = indicators.voter_turnout(path)
    assert tuples(frame) == [
        (dt(1992, 1, 1), 75.2),
        (dt(1996, 1, 1), 52.9),
        (dt(2000, 1, 1), 58.2),
        (dt(2004, 1, 1), 46.0),
        (dt(2008, 1, 1), 48.6),
        (dt(2012, 1, 1), 52.9),
    ]
