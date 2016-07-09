# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_auto_20150723_0352'),
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('slug', autoslug.fields.AutoSlugField(editable=False)),
                ('name', models.CharField(max_length=255)),
                ('profession', models.CharField(blank=True, choices=[('', 'Nenurodyta'), ('advokatas', 'Advokatas'), ('agronomas', 'Agronomas'), ('aktorius', 'Aktorius'), ('archeologas', 'Archeologas'), ('architektas', 'Architektas'), ('atstovas spaudai', 'Atstovas Spaudai'), ('auditorius', 'Auditorius'), ('bendrosios praktikos slaugytojas', 'Bendrosios Praktikos Slaugytojas'), ('bibliotekininkas', 'Bibliotekininkas'), ('biologas', 'Biologas'), ('buhalteris', 'Buhalteris'), ('chemikas', 'Chemikas'), ('dailininkas', 'Dailininkas'), ('dietologas', 'Dietologas'), ('drabužių dizaineris', 'DrabužIų Dizaineris'), ('dėstytojas', 'Dėstytojas'), ('ekonomistas', 'Ekonomistas'), ('filosofas', 'Filosofas'), ('finansininkas', 'Finansininkas'), ('fizikas', 'Fizikas'), ('geologas', 'Geologas'), ('gydytojas', 'Gydytojas'), ('inžinierius', 'InžInierius'), ('istorikas', 'Istorikas'), ('kartografas', 'Kartografas'), ('konstruktorius', 'Konstruktorius'), ('matematikas', 'Matematikas'), ('meteorologas', 'Meteorologas'), ('mokytojas', 'Mokytojas'), ('muzikantas', 'Muzikantas'), ('prodiuseris', 'Prodiuseris'), ('programuotojas', 'Programuotojas'), ('prokuroras', 'Prokuroras'), ('psichologas', 'Psichologas'), ('rašytojas', 'RašYtojas'), ('socialinis darbuotojas', 'Socialinis Darbuotojas'), ('statistikas', 'Statistikas'), ('teisininkas', 'Teisininkas'), ('vaistininkas', 'Vaistininkas'), ('vertėjas', 'Vertėjas'), ('viešojo administravimo specialistas', 'ViešOjo Administravimo Specialistas'), ('zoologas', 'Zoologas'), ('žinių pranešėjas', 'ŽInių PranešĖjas'), ('žurnalistas', 'ŽUrnalistas')], max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Quote',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('quote', models.TextField(verbose_name='Citata')),
                ('link', models.URLField(blank=True, verbose_name='Nuoroda')),
                ('source', models.CharField(blank=True, max_length=255, verbose_name='Šaltinis')),
                ('timestamp', models.DateTimeField(null=True, blank=True, verbose_name='Data')),
                ('timestamp_display', models.PositiveSmallIntegerField(choices=[(0, 'Nėra'), (1, 'Metai'), (2, 'Mėnuo'), (3, 'Diena'), (4, 'Valanda'), (5, 'Minutė'), (6, 'Sekundė')])),
                ('person', models.ForeignKey(to='website.Person')),
            ],
        ),
        migrations.AddField(
            model_name='position',
            name='person',
            field=models.ForeignKey(null=True, blank=True, to='website.Person'),
        ),
        migrations.AddField(
            model_name='vote',
            name='person',
            field=models.ForeignKey(null=True, blank=True, to='website.Person'),
        ),
    ]
