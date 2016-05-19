import pandas as pd


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

    return frame, {
        'title': 'Rinkimuose dalyvavusių rinkėjų skaičius, palyginti su visų rinkėjų skaičiumi',
        'ylabel': 'Aktyvumas procentais',
    }


INDICATORS = [
    ('voter_turnout', 'seimas.indicators.voter_turnout'),
]
