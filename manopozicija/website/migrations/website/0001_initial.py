# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields
import django_extensions.db.fields
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('weight', models.PositiveSmallIntegerField(default=1)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(editable=False, default=django.utils.timezone.now, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(editable=False, default=django.utils.timezone.now, blank=True)),
                ('slug', autoslug.fields.AutoSlugField(editable=False)),
                ('title', models.CharField(max_length=255, verbose_name='Pavadinimas')),
                ('description', models.TextField(verbose_name='Aprašymas', blank=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('link', models.URLField()),
                ('fraction', models.CharField(max_length=255)),
                ('position', models.PositiveSmallIntegerField(choices=[(0, 'Nebalsavo'), (1, 'Už'), (2, 'Prieš'), (3, 'Susilaikė')], default=0)),
                ('score', models.SmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Voting',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(editable=False, default=django.utils.timezone.now, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(editable=False, default=django.utils.timezone.now, blank=True)),
                ('title', models.CharField(max_length=255, verbose_name='Pavadinimas')),
                ('link', models.URLField(verbose_name='Nuoroda')),
                ('description', models.TextField(verbose_name='Aprašymas', blank=True)),
                ('datetime', models.DateTimeField(null=True, blank=True)),
                ('vid', models.CharField(max_length=20, verbose_name='Balsavimo ID', blank=True)),
                ('question', models.CharField(max_length=255, verbose_name='Klausimas', blank=True)),
                ('question_a', models.CharField(max_length=255, verbose_name='Klausimas A', blank=True)),
                ('question_b', models.CharField(max_length=255, verbose_name='Klausimas B', blank=True)),
                ('result', models.CharField(max_length=40, verbose_name='Rezultatas', blank=True)),
                ('sitting_no', models.CharField(max_length=40, verbose_name='Posėdžio Nr.', blank=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='vote',
            name='voting',
            field=models.ForeignKey(to='website.Voting'),
        ),
        migrations.AddField(
            model_name='position',
            name='topic',
            field=models.ForeignKey(to='website.Topic'),
        ),
    ]
