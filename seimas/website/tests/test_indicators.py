import datetime
import pkg_resources as pres

from seimas import indicators

dt = datetime.datetime


def tuples(frame):
    return list(map(tuple, frame.to_records()))


def test_voter_turnout():
    path = pres.resource_filename('seimas.website.tests', 'fixtures/indicators/voter_turnout.tsv.gz')
    frame, meta = indicators.voter_turnout(path)
    assert tuples(frame) == [
        (dt(1992, 1, 1), 75.2),
        (dt(1996, 1, 1), 52.9),
        (dt(2000, 1, 1), 58.2),
        (dt(2004, 1, 1), 46.0),
        (dt(2008, 1, 1), 48.6),
        (dt(2012, 1, 1), 52.9),
    ]
