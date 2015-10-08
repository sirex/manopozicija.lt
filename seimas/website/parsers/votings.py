import bs4
import re
import datetime
import urllib.parse

from seimas.website.lists import get_first_names


SPACES_RE = re.compile(r'\s+')

POSITION_MAP = {
    0: 'aye',
    1: 'no',
    2: 'abstain',
}


def contains(string):
    def func(s):
        if s:
            return string.lower() in SPACES_RE.sub(' ', s.lower())
        else:
            return False
    return func


def get_position(cols):
    if '+' in cols:
        return POSITION_MAP[cols.index('+')]
    else:
        return 'no-vote'


def get_voting_id(url):
    query = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(url).query))
    return query['p_bals_id']


def norm_name(full_name):
    first_name = []
    last_name = []
    first_names = get_first_names()
    for name in full_name.split():
        if name.lower() in first_names:
            first_name.append(name)
        else:
            last_name.append(name)

    if not first_name:
        raise ValueError('Could not detect first iname for "%s".' % full_name)

    return ' '.join(first_name) + ' ' + ' '.join(last_name)


def parse_votes(url, html):
    result = {
        'id': get_voting_id(url),
        'url': url,
    }

    soup = bs4.BeautifulSoup(html)

    node = soup.find(string=contains('Seimo posėdis Nr.'))
    result['sitting_no'] = int(node.strip()[len('Seimo posėdis Nr.'):].strip())

    node = node.parent.find_next('a')
    date = node.string

    node = soup.find(string=contains('Formuluotė:'))
    if node is None:
        result['question'] = ''

        node = soup.find(string=contains('Formuluotė A:')).find_next('b')
        result['question_a'] = node.string

        node = node.find_next(string=contains('Formuluotė B:')).find_next('b')
        result['question_b'] = node.string

    else:
        node = node.find_next('b')
        result['question'] = node.string

        result['question_a'] = ''
        result['question_b'] = ''

    node = node.find_next(string=contains('Balsavimo laikas:')).find_next('b')
    result['datetime'] = datetime.datetime.strptime('%sT%s' % (date, node.string), '%Y-%m-%dT%H:%M:%S')

    node = node.find_next(string=contains('Balsavo Seimo narių:')).find_next('b')
    result['votes'] = int(node.string)

    node = node.find_next(string=contains('iš')).find_next('b')
    result['total'] = int(node.string)

    node = node.find_next(string=contains('Balsavimo rezultatai:')).find_next('b')
    result['aye'] = int(node.string)

    if result['question_a']:
        node = node.find_next(string=contains('B -')).find_next('b')
        result['no'] = int(node.string)
    else:
        node = node.find_next(string=contains('prieš')).find_next('b')
        result['no'] = int(node.string)

    node = node.find_next(string=contains('susilaikė')).find_next('b')
    result['abstain'] = int(node.string)

    node = node.find_next('b')
    result['result'] = node.string

    if result['question_a']:
        table_title = 'Individualūs alternatyvaus balsavimo rezultatai'
    else:
        table_title = 'Individualūs balsavimo rezultatai'

    result['table'] = []
    table = soup.find('h4', string=contains(table_title)).parent.find_next('table')
    for row in table('tr'):
        cols = row('td')
        if len(cols) == 5:
            result['table'].append({
                'link': cols[0].a['href'],
                'name': norm_name(cols[0].a.string.strip()),
                'fraction': cols[1].string.strip(),
                'position': get_position([x.string.strip() for x in cols[2:]]),
            })

    return result
