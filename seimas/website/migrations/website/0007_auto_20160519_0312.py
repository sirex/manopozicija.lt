# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0006_auto_20151009_0512'),
    ]

    operations = [
        migrations.CreateModel(
            name='Indicator',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('slug', models.SlugField(unique=True, editable=False)),
                ('created', django_extensions.db.fields.CreationDateTimeField(editable=False, blank=True, default=django.utils.timezone.now)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(editable=False, blank=True, default=django.utils.timezone.now)),
                ('deleted', models.DateTimeField(editable=False, blank=True, null=True)),
                ('last_update', models.DateTimeField(editable=False, blank=True, null=True)),
                ('update_freq', models.PositiveIntegerField(default=86400)),
                ('title', models.CharField(max_length=255)),
                ('ylabel', models.CharField(max_length=255)),
            ],
        ),
        migrations.AlterField(
            model_name='quote',
            name='timestamp_display',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Nėra'), (1, 'Metai'), (2, 'Mėnuo'), (3, 'Diena'), (4, 'Valanda'), (5, 'Minutė'), (6, 'Sekundė')], default=3),
        ),
    ]
