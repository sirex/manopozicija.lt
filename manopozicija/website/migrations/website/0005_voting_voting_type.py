# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_auto_20150723_0842'),
    ]

    operations = [
        migrations.AddField(
            model_name='voting',
            name='voting_type',
            field=models.PositiveSmallIntegerField(default=2, choices=[(1, 'Seimo'), (2, 'Savivaldybės')]),
        ),
    ]
