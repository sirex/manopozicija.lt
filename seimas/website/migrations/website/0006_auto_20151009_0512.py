# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0005_voting_voting_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='quote',
            name='description',
            field=models.TextField(blank=True, verbose_name='Aprašymas'),
        ),
        migrations.AddField(
            model_name='quote',
            name='title',
            field=models.CharField(verbose_name='Pavadinimas', default='', max_length=255),
            preserve_default=False,
        ),
    ]
