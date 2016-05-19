import datetime
import pandas as pd

from seimas.website.models import Indicator


def voter_turnout(source=(
    'http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?file=data/tsdgo310.tsv.gz'
)):
    frame = pd.read_csv(
        source,
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
    frame[0] = frame[0].astype(float)
    frame = frame.rename(columns={0: 'Seimo'})

    return frame


INDICATORS = [
    ('voter-turnout', {
        'fetch': 'seimas.indicators.voter_turnout',
        'title': 'Rinkimuose dalyvavusių rinkėjų skaičius, palyginti su visų rinkėjų skaičiumi',
        'ylabel': 'Aktyvumas procentais',
    }),
]


def import_indicators(indicators):
    """Import all defined indicators to database."""
    deleted_indicators = set()
    existing_indicators = set(Indicator.objects.values_list('pk', flat=True))
    for name, params in indicators:
        params = {k: v for k, v in params.items() if k != 'fetch'}
        indictor, created = Indicator.objects.get_or_create(slug=name, defaults=params)
        if indictor.pk in existing_indicators:
            existing_indicators.remove(indictor.pk)
        if indictor.deleted:
            deleted_indicators.add(indictor.pk)
    # Mark no longer existing indicators as deleted
    if existing_indicators:
        Indicator.objects.filter(pk__in=existing_indicators).update(deleted=datetime.datetime.utcnow())
    # Clear deletion flag for resurected indicators
    if deleted_indicators:
        Indicator.objects.filter(pk__in=deleted_indicators).update(deleted=None)


def update_indicators(indicators):
    for indicator in indicators:
        pass
