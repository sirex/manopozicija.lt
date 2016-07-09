import io
import mock
import datetime
import pytest
import pkg_resources as pres
import pandas as pd

from manopozicija import indicators
from manopozicija.website.models import Indicator

dt = datetime.datetime
timedelta = datetime.timedelta


def ls(base, path):
    return sorted([(x).relto(base) for x in path.listdir()])


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


@pytest.mark.django_db
def test_update_indicators(settings, tmpdir):
    if not settings.DATABASES['default']['ENGINE'].startswith('django.db.backends.postgresql'):
        pytest.skip('postgresql only')

    settings.MEDIA_ROOT = tmpdir.strpath

    now = datetime.datetime(2016, 1, 1, 0, 0, 0)
    frame = pd.DataFrame([(1, 0.1), (2, 0.2)], columns=['datetime', 'y']).set_index('datetime', drop=True)

    # Update, because last_update is None
    Indicator.objects.create(slug='a', update_freq=10, last_update=None)
    # Do not update, because it was updated 5 seconds ago and update frequency is 10 seconds
    Indicator.objects.create(slug='b', update_freq=10, last_update=now - timedelta(seconds=5))
    # Update, because it was updated 20 seconds ago and update frequency is 10 seconds
    Indicator.objects.create(slug='c', update_freq=10, last_update=now - timedelta(seconds=20))
    # Do not update, because error count is greather than 10
    Indicator.objects.create(slug='d', update_freq=10, last_update=now - timedelta(seconds=20), error_count=20)

    indicators_ = [
        ('a', {'fetch': mock.Mock(return_value=frame)}),
        ('b', {'fetch': mock.Mock(return_value=frame)}),
        ('c', {'fetch': mock.Mock(return_value=frame)}),
        ('d', {'fetch': mock.Mock(return_value=frame)}),
    ]

    indicators.update_indicators(indicators_, now)

    indicator = Indicator.objects.get(slug='a')
    assert indicator.error_count == 0
    assert indicator.traceback == ''
    assert indicator.last_update >= now
    assert ls(tmpdir, tmpdir / 'indicators') == [
        'indicators/a.csv',
        'indicators/c.csv',
    ]
    assert tuples(pd.read_csv(str(tmpdir / 'indicators/a.csv'), index_col=0)) == [
        (1, 0.1),
        (2, 0.2),
    ]


@pytest.mark.django_db
def test_update_indicators_error(settings, tmpdir):
    if not settings.DATABASES['default']['ENGINE'].startswith('django.db.backends.postgresql'):
        pytest.skip('postgresql only')

    settings.MEDIA_ROOT = tmpdir.strpath

    Indicator.objects.create(slug='a', last_update=None, update_freq=10)

    now = datetime.datetime(2016, 1, 1, 0, 0, 0)
    indicators_ = [('a', {'fetch': mock.Mock(side_effect=Exception())})]
    indicators.update_indicators(indicators_, now)
    indicator = Indicator.objects.get(slug='a')
    assert indicator.error_count == 1
    assert indicator.traceback != ''
    assert indicator.last_update is None
    assert ls(tmpdir, tmpdir / 'indicators') == []


def test_voter_turnout():
    path = pres.resource_filename('manopozicija.website.tests', 'fixtures/indicators/voter_turnout.tsv.gz')
    frame = indicators.voter_turnout({'source': path})

    assert tuples(frame) == [
        (dt(1992, 1, 1), 75.2),
        (dt(1996, 1, 1), 52.9),
        (dt(2000, 1, 1), 58.2),
        (dt(2004, 1, 1), 46.0),
        (dt(2008, 1, 1), 48.6),
        (dt(2012, 1, 1), 52.9),
    ]

    output = io.StringIO()
    frame.to_csv(output)
    assert output.getvalue() == '\n'.join([
        'datetime,Seimo',
        '1992-01-01,75.2',
        '1996-01-01,52.9',
        '2000-01-01,58.2',
        '2004-01-01,46.0',
        '2008-01-01,48.6',
        '2012-01-01,52.9',
        '',
    ])
