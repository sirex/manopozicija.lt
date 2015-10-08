import csv
import io
from unittest import TestCase

from django_webtest import WebTest

from django.contrib.auth.models import User

from seimas.website.models import Topic
from seimas.website.models import Voting
from seimas.website.models import Vote
from seimas.website.models import Person


class ViewTests(TestCase):

    def test_import_voitings(self):
        '''Import voitings from questions.csv file'''
        votings_str = '"31213";"DĖL VILNIAUS MIESTO SAVIVALDYBĖS KONTROLIUOJAMŲ AKCINIŲ BENDROVIŲ IR UŽDARŲJŲ AKCINIŲ BENDROVIŲ STEBĖTOJŲ TARYBŲ SUDĖČIŲ TVIRTINIMO";"b8f7d8f0e9c411e4b95b822bbd2437dd";" 9. SVARSTYTA. D&#278;L VILNIAUS MIESTO SAVIVALDYB&#278;S KONTROLIUOJAM&#370; AKCINI&#370; BENDROVI&#370; IR U&#381;DAR&#370;J&#370; AKCINI&#370; BENDROVI&#370; STEB&#278;TOJ&#370; TARYB&#370; SUD&#278;&#268;I&#370; TVIRTINIMO.";"9";"40263390";"2";"6034";"50";"2015-04-23 13:28:22";"2";;"0";"0";;"905744af65159f62f27e33e9b3c92a33";\n'\
                      '"31214";"DĖL VILNIAUS MIESTO SAVIVALDYBĖS TARYBOS ADMINISTRACINĖS KOMISIJOS SUDARYMO";"e04900a0e9c411e4b95b822bbd2437dd";" 10. SVARSTYTA. D&#278;L VILNIAUS MIESTO SAVIVALDYB&#278;S TARYBOS ADMINISTRACIN&#278;S KOMISIJOS SUDARYMO.";"10";"40263390";"2";"6043";"50";"2015-04-23 13:28:22";"2";;"0";"0";;"2c12f164f03690e31146f8d8580c74a9";\n'\
                      '"28144";"Dėl 2012-01-24 posėdžio darbotvarkės projekto tvirtinimo";"908c3be0466b11e1acacd94099a47d4a";" 2. SVARSTYTA. D&#279;l 2012-01-24 pos&#279;d&#382;io darbotvark&#279;s projekto tvirtinimo.";"2";"10504907";"2";"0";"50";"2012-01-24 11:00:43";"2";;"0";"0";;"5c6006c5420433a2a51ea7235296a4f6";\n'\
                      '"28215";"Dėl Balsų skaičiavimo komisijos tvirtinimo";"0749c1b0684211e1a18389f4596ac3a6";" 1. SVARSTYTA. D&#279;l Bals&#371; skai&#269;iavimo komisijos tvirtinimo. ";"1";"10709735";"2";"0";"50";"2012-02-28 12:08:21";"2";;"0";"0";;"5c6006c5420433a2a51ea7235296a4f6";'

        with io.StringIO(votings_str) as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            for voting_args in reader:
                qid = int(voting_args[0])
                title = voting_args[1]
                description = voting_args[3]
                Voting.objects.create(title=title, description=description, vid=qid)

        self.assertEqual(Voting.objects.get(vid=31213).title, "DĖL VILNIAUS MIESTO SAVIVALDYBĖS KONTROLIUOJAMŲ AKCINIŲ BENDROVIŲ IR UŽDARŲJŲ AKCINIŲ BENDROVIŲ STEBĖTOJŲ TARYBŲ SUDĖČIŲ TVIRTINIMO")
        self.assertTrue(Voting.objects.get(vid=31214).title.startswith("DĖL VILNIAUS MIESTO SAVIVALDYBĖS"))

        meetings_str = '"10709735";"VILNIAUS MIESTO SAVIVALDYBĖS TARYBOS POSĖDIS NR.18";"250059c061f411e1a724f54077dd31a2";"1";;"2012-03-07 14:00:00";"2012-02-28 12:08:21";"50";"Zuzana Žičienė&lt;br/&gt;&lt;br/&gt;Tarybos sekretoriatas Skyriaus vedėjo pavaduotojas, Kontrolės komitetas Vedėjo pavaduotojas &lt;br/&gt;&lt;a href=&quot;mailto:zuzana.ziciene@vilnius.lt&quot;&gt;zuzana.ziciene@vilnius.lt&lt;/a&gt; &lt;br/&gt;Konstitucijos pr. 3, LT-09601 Vilnius, 213 kab., telefonas 211 2549&lt;br/&gt;211 2151, 680 61151";"Zuzana Žičienė";"50";"5671";"1";"Artūras Zuokas&lt;br/&gt;&lt;br/&gt;Strateginio planavimo komisija Pirmininkas, Meras Meras, Vilniaus miesto savivaldybės taryba Tarybos narys, Frakcija „TAIP!“ Narys &lt;br/&gt;&lt;a href=&quot;mailto:meras@vilnius.lt&quot;&gt;meras@vilnius.lt&lt;/a&gt; &lt;br/&gt;Konstitucijos pr. 3, LT-09601, Vilnius,  312 kab., tel.  (8 5) 211 2781&lt;br/&gt;211 2889";"Artūras Zuokas";;;"162adc73cbd6ae3327388db5bbaed1e7";;;'
        votes_str = '"248";"Už";"28215";"10709735";"Pirmininkas";"Pirmininkas";"2012-03-07 14:13:48";"Už";"1"\n'\
                    '"60989";"Prieš";"31213";"40263390";"A. Zuokas";"A. Zuokas";"2015-04-29 14:51:58";"Prieš";"3"\n'\
                    '"60971";"Už";"31213";"40263390";"R. Šimašius";"R. Šimašius";"2015-04-29 14:51:58";"Už";"1"\n'\
                    '"60972";"Už";"31213";"40263390";"G. Švilpa";"G. Švilpa";"2015-04-29 14:51:58";"Už";"1"\n'\
                    '"60994";"Už";"31214";"40263390";"Šimašius";"Šimašius";"2015-04-29 14:54:27";"Už";"1"\n'

        with io.StringIO(votes_str) as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            for vote_args in reader:
                qid = int(vote_args[2])
                voting = Voting.objects.get(vid=qid)
                meeting_id = int(vote_args[3])
                person_str = vote_args[5]
                person = Person.objects.get_or_create(person_str, meeting_id, io.StringIO(meetings_str))
                date_str = vote_args[6]
                vote_str = vote_args[7]
                vote = Vote.objects.get_vote_id(vote_str)
                Vote.objects.create(voting=voting, person=person, vote=vote)

        self.assertEqual(Vote.objects.count(), 5)
        self.assertEqual(Vote.objects.filter(voting__vid=31213).count(), 3)
        self.assertEqual(Vote.objects.filter(voting__vid=31214).count(), 1)
