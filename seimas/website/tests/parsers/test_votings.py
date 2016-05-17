import unittest
import pkg_resources as pres
import datetime

from seimas.website.parsers.votings import parse_votes


class ParseVotesTests(unittest.TestCase):

    def test_bals_18573(self):
        url = 'http://www3.lrs.lt/pls/inter/w5_sale.bals?p_bals_id=18573'
        html = pres.resource_string('seimas.website.tests', 'fixtures/bals18573.html')
        result = parse_votes(url, html)
        table = result.pop('table')

        self.assertEqual(result, {
            'abstain': 11,
            'aye': 51,
            'datetime': datetime.datetime(2006, 11, 16, 16, 59, 44),
            'id': '18573',
            'no': 7,
            'question': 'dėl Seimo nutarimo priėmimo',
            'question_a': '',
            'question_b': '',
            'result': 'pritarta',
            'sitting_no': 236,
            'total': 141,
            'url': 'http://www3.lrs.lt/pls/inter/w5_sale.bals?p_bals_id=18573',
            'votes': 69,
        })

        self.assertEqual(table[0], {
            'fraction': 'TTF',
            'link': 'http://www3.lrs.lt/docs3/kad5/w5_istorija.show5-p_r=786&p_k=1&p_a=5&p_asm_id=47852.html',
            'name': 'Remigijus Ačas',
            'position': 'no',
        })

        self.assertEqual(result['total'], len(table))
        self.assertEqual(result['votes'], len([x for x in table if x['position'] != 'no-vote']))
        self.assertEqual(result['aye'], len([x for x in table if x['position'] == 'aye']))
        self.assertEqual(result['no'], len([x for x in table if x['position'] == 'no']))
        self.assertEqual(result['abstain'], len([x for x in table if x['position'] == 'abstain']))

    def test_bals_9466(self):
        url = 'http://www3.lrs.lt/pls/inter/w5_sale.bals?p_bals_id=-9466'
        html = pres.resource_string('seimas.website.tests', 'fixtures/bals-9466.html')
        result = parse_votes(url, html)
        table = result.pop('table')

        self.assertEqual(result, {
            'abstain': 25,
            'aye': 29,
            'datetime': datetime.datetime(2010, 9, 28, 17, 59, 49),
            'id': '-9466',
            'no': 9,
            'question': 'dėl pritarimo po pateikimo',
            'question_a': '',
            'question_b': '',
            'result': 'nepritarta',
            'sitting_no': 251,
            'total': 140,
            'url': 'http://www3.lrs.lt/pls/inter/w5_sale.bals?p_bals_id=-9466',
            'votes': 63,
        })

        self.assertEqual(table[0], {
            'fraction': 'TTF',
            'link': 'http://www3.lrs.lt/pls/inter/w5_show?p_r=6113&p_k=1&p_a=5&p_asm_id=47852&p_kade_id=6',
            'name': 'Remigijus Ačas',
            'position': 'no',
        })

        self.assertEqual(result['total'], len(table))
        self.assertEqual(result['votes'], len([x for x in table if x['position'] != 'no-vote']))
        self.assertEqual(result['aye'], len([x for x in table if x['position'] == 'aye']))
        self.assertEqual(result['no'], len([x for x in table if x['position'] == 'no']))
        self.assertEqual(result['abstain'], len([x for x in table if x['position'] == 'abstain']))

    def test_bals_1132(self):
        url = 'http://www3.lrs.lt/pls/inter/w5_sale.bals?p_bals_id=-1132'
        html = pres.resource_string('seimas.website.tests', 'fixtures/bals-1132.html')
        result = parse_votes(url, html)
        table = result.pop('table')

        self.maxDiff = None

        self.assertEqual(result, {
            'abstain': 0,
            'aye': 33,
            'datetime': datetime.datetime(2008, 1, 17, 18, 2, 5),
            'id': '-1132',
            'no': 44,
            'question': '',
            'question_a': 'už siūlymą grąžinti projektą Nr.XP-2194(2*) iniciatoriams tobulinti',
            'question_b': 'už siūlymą jį atmesti',
            'result': 'pritarta formuluotei B',
            'sitting_no': 376,
            'total': 141,
            'url': 'http://www3.lrs.lt/pls/inter/w5_sale.bals?p_bals_id=-1132',
            'votes': 77,
        })

        self.assertEqual(table[0], {
            'fraction': 'TTF',
            'link': 'http://www3.lrs.lt/docs3/kad5/w5_istorija.show5-p_r=786&p_k=1&p_a=5&p_asm_id=47852.html',
            'name': 'Remigijus Ačas',
            'position': 'no',
        })

        self.assertEqual(result['total'], len(table))
        self.assertEqual(result['votes'], len([x for x in table if x['position'] != 'no-vote']))
        self.assertEqual(result['aye'], len([x for x in table if x['position'] == 'aye']))
        self.assertEqual(result['no'], len([x for x in table if x['position'] == 'no']))
        self.assertEqual(result['abstain'], len([x for x in table if x['position'] == 'abstain']))
