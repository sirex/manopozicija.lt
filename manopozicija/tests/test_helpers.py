from manopozicija import factories
from manopozicija import services
from manopozicija import helpers


def test_get_arguments(app):
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
    assert helpers.get_arguments(services.get_topic_arguments(topic)) == [
        (
            {'count': 1, 'position': +1, 'title': 'didesnis užsienio lietuvių aktyvumas rinkimuose'},
            {'count': 2, 'position': -1, 'title': 'balsų pirkimas'},
        ),
        (
            {'count': 1, 'position': +1, 'title': 'šiuolaikiška, modernu'},
            {'count': 1, 'position': -1, 'title': 'balsavimas nekontroliuojamoje aplinkoje'},
        )
    ]
