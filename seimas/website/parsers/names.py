import bs4
import unicodedata


def parse_index(html):
    soup = bs4.BeautifulSoup(html)
    menu = soup.find('ul', id='siteMenu')

    result = []
    for item in menu('li'):
        result.append(item.a['href'])

    return result


def parse_names(html):
    soup = bs4.BeautifulSoup(html)
    index = soup.find('ul', 'namesList')

    result = []

    for link in index('a', 'mName'):
        result.append(('m', strip_accents(link.string)))

    for link in index('a', 'fName'):
        result.append(('f', strip_accents(link.string)))

    return result


def strip_accents(string, accents=('COMBINING ACUTE ACCENT', 'COMBINING GRAVE ACCENT', 'COMBINING TILDE')):
    accents = set(map(unicodedata.lookup, accents))
    chars = [c for c in unicodedata.normalize('NFD', string) if c not in accents]
    return unicodedata.normalize('NFC', ''.join(chars))
