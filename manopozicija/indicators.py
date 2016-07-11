import logging
import os.path
import datetime
import traceback
import pandas as pd

from django.conf import settings
from django.db.models import Func, F, Q

from manopozicija.models import Indicator

logger = logging.getLogger(__name__)


def get_params(params, defaults):
    params = dict(params or {})
    for key, value in defaults.items():
        params.setdefault(key, value)
    return params


def voter_turnout(params=None):
    params = get_params(params, {
        'source': 'http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?file=data/tsdgo310.tsv.gz',
    })

    frame = pd.read_csv(
        params['source'],
        sep='\t',
        compression='gzip',
        index_col=0,
        na_values=[': '],
    )

    frame = (
        frame.stack().
        loc['NAT_VOTE,LT', :].to_frame().
        reset_index(level=0, drop=True)
    )

    frame.index = pd.to_datetime(frame.index.str.strip(), format='%Y')
    frame.index.name = 'datetime'
    frame[0] = frame[0].astype(float)
    frame = frame.rename(columns={0: 'Seimo'})

    return frame


INDICATORS = [
    ('voter-turnout', {
        'fetch': voter_turnout,
        'title': 'Rinkimuose dalyvavusių rinkėjų skaičius, palyginti su visų rinkėjų skaičiumi',
        'ylabel': 'Aktyvumas procentais',
        'source': 'http://ec.europa.eu/eurostat/tgm/table.do?tab=table&init=1&language=en&pcode=tsdgo310&plugin=1',
    }),
]


def import_indicators(indicators):
    """Import all defined indicators to database."""
    deleted_indicators = set()
    existing_indicators = set(Indicator.objects.values_list('pk', flat=True))
    for name, params in indicators:
        params = {k: v for k, v in params.items() if k != 'fetch'}
        indicator, created = Indicator.objects.get_or_create(slug=name, defaults=params)
        if indicator.pk in existing_indicators:
            existing_indicators.remove(indicator.pk)
        if indicator.deleted:
            deleted_indicators.add(indicator.pk)
        updated = False
        for key, value in params.items():
            if not getattr(indicator, key):
                setattr(indicator, key, value)
                updated = True
        if updated:
            indicator.save()
    # Mark no longer existing indicators as deleted
    if existing_indicators:
        Indicator.objects.filter(pk__in=existing_indicators).update(deleted=datetime.datetime.utcnow())
    # Clear deletion flag for resurected indicators
    if deleted_indicators:
        Indicator.objects.filter(pk__in=deleted_indicators).update(deleted=None)


class SecondsSince(Func):
    template = "%(now)d - DATE_PART('epoch', %(expressions)s)::int"


def update_indicators(indicators, now=None):
    indicators_dir = os.path.join(settings.MEDIA_ROOT, 'indicators')
    if not os.path.exists(indicators_dir):
        os.mkdir(indicators_dir)

    now_ = datetime.datetime.utcnow()
    now = now or now_

    indicators = dict(indicators)

    qs = Indicator.objects.filter(
        Q(last_update__isnull=True) | Q(update_freq__lt=SecondsSince(F('last_update'), now=int(now.timestamp()))),
        deleted__isnull=True,  # only non-deleted objects
        error_count__lt=10,  # don't try to fetch indicators who returned error 10 times in a row
    )

    for indicator in qs:
        params = indicators[indicator.slug]
        fetch = params['fetch']
        try:
            frame = fetch()
        except Exception:
            logger.exception('error while updating %r indicator' % indicator.slug)
            indicator.error_count = indicator.error_count + 1
            indicator.traceback = traceback.format_exc()
            indicator.save()
        else:
            frame.to_csv(os.path.join(indicators_dir, '%s.csv' % indicator.slug))
            indicator.error_count = 0
            indicator.traceback = ''
            indicator.last_update = now + (datetime.datetime.utcnow() - now_)
            indicator.save()


def get_indicator_data(indicator):
    indicators_dir = os.path.join(settings.MEDIA_ROOT, 'indicators')
    frame = pd.read_csv(os.path.join(indicators_dir, '%s.csv' % indicator.slug), index_col=0)
    return list(map(list, frame.to_records()))
