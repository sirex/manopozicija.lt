import pkg_resources as pres


def read_first_names():
    path = pres.resource_filename('manopozicija', 'data/names.tsv')
    with open(path) as f:
        for line in f:
            gender, name = line.strip().split('\t')
            yield name.lower()


_first_names = None


def get_first_names():
    global _first_names
    if _first_names is None:
        _first_names = list(read_first_names())
    return _first_names
