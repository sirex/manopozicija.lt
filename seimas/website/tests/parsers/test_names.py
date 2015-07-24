import unittest
import pkg_resources as pres

from seimas.website.parsers.names import parse_index, parse_names, strip_accents


class ParseNamesTests(unittest.TestCase):

    def test_parse_index(self):
        html = pres.resource_string('seimas.website.tests', 'fixtures/names_index.html')
        result = parse_index(html)
        self.assertEqual(result[0], 'http://vardai.vlkk.lt/sarasas/a/')
        self.assertEqual(len(result), 25)

    def test_parse_names(self):
        html = pres.resource_string('seimas.website.tests', 'fixtures/names_page.html')
        result = parse_names(html)
        self.assertEqual(result[:2], [('m', 'Abdonas'), ('m', 'Abdula')])


class RemoveAccentsTests(unittest.TestCase):

    def test_remove_accents(self):
        self.assertEqual(strip_accents('Abdulà'), 'Abdula')
        self.assertEqual(strip_accents('Ãdė'), 'Adė')
        self.assertEqual(strip_accents('Arė́ja'), 'Arėja')
        self.assertEqual(strip_accents('Ą́žuolas'), 'Ąžuolas')
        self.assertEqual(strip_accents('~'), '~')
