import datetime

from manopozicija import services
from manopozicija import factories


def test_get_topic_arguments(app):
    arguments = [
        (+1, False, 'didesnis užsienio lietuvių aktyvumas rinkimuose'),
        (+1, True, 'šiuolaikiška, modernu'),
        (+1, False, 'šiuolaikiška, modernu'),
        (-1, False, 'balsavimas nekontroliuojamoje aplinkoje'),
        (-1, True, 'balsų pirkimas'),
        (-1, False, 'balsų pirkimas'),
        (-1, False, 'balsų pirkimas'),
    ]
    topic = factories.TopicFactory()
    for position, counterargument, argument in arguments:
        factories.ArgumentFactory(topic=topic, position=position, title=argument, counterargument=counterargument)
    assert list(services.get_topic_arguments(topic).values_list('count', 'position', 'title')) == [
        (2, -1, 'balsų pirkimas'),
        (1, 1, 'didesnis užsienio lietuvių aktyvumas rinkimuose'),
        (1, -1, 'balsavimas nekontroliuojamoje aplinkoje'),
        (1, 1, 'šiuolaikiška, modernu'),
    ]


def test_get_topic_posts(app):
    topic = factories.TopicFactory()
    factories.create_topic_posts(topic, [
        ('event', 1, 0, 'Balsavimo internetu koncepcijos patvirtinimas', 'lrs.lt', '2006-11-26'),
        ('quote', 'Mantas Adomėnas', 'seimo narys', 'kauno.diena.lt', '2016-03-22', [
            (4, 0, 'Nepasiduokime paviršutiniškiems šūkiams – šiuolaikiška, modernu.', [
                (1, 'šiuolaikiška, modernu', True),
            ]),
            (0, 0, 'Atidaroma galimybė prekiauti balsais ir likti nebaudžiamam.', [
                (-1, 'balsų pirkimas', None),
            ]),
        ]),
    ])
    assert services.dump_topic_posts(topic) == '\n'.join([
        '( ) (n) Mantas Adomėnas (seimo narys)                                          kauno.diena.lt 2016-03-22    ',
        ' |      Nepasiduokime paviršutiniškiems šūkiams – šiuolaikiška, modernu.                                 (4)',
        ' |      - (y) šiuolaikiška, modernu < (counterargument)                                                     ',
        ' |      Atidaroma galimybė prekiauti balsais ir likti nebaudžiamam.                                      (0)',
        ' |      - (n) balsų pirkimas                                                                                ',
        ' |                                                                                                          ',
        ' o  (-) Balsavimo internetu koncepcijos patvirtinimas                                  lrs.lt 2006-11-26 (1)',
    ])
