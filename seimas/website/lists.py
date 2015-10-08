import pkg_resources as pres


professions = [
    'advokatas',
    'agronomas',
    'aktorius',
    'archeologas',
    'architektas',
    'atstovas spaudai',
    'auditorius',
    'bendrosios praktikos slaugytojas',
    'bibliotekininkas',
    'biologas',
    'buhalteris',
    'chemikas',
    'dailininkas',
    'dietologas',
    'drabužių dizaineris',
    'dėstytojas',
    'ekonomistas',
    'filosofas',
    'finansininkas',
    'fizikas',
    'geologas',
    'gydytojas',
    'inžinierius',
    'istorikas',
    'kartografas',
    'konstruktorius',
    'matematikas',
    'meteorologas',
    'mokytojas',
    'muzikantas',
    'prodiuseris',
    'programuotojas',
    'prokuroras',
    'psichologas',
    'rašytojas',
    'socialinis darbuotojas',
    'statistikas',
    'teisininkas',
    'vaistininkas',
    'vertėjas',
    'viešojo administravimo specialistas',
    'zoologas',
    'žinių pranešėjas',
    'žurnalistas',
]


def read_first_names():
    path = pres.resource_filename('seimas', 'data/names.tsv')
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
