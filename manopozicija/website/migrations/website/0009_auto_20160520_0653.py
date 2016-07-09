# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0008_auto_20160519_0658'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicator',
            name='source',
            field=models.URLField(default='', verbose_name='Šaltinis'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='indicator',
            name='update_freq',
            field=models.PositiveIntegerField(default=86400, help_text='Indicator update frequency in seconds (86400 == 1 day).'),
        ),
    ]
