# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0007_auto_20160519_0312'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicator',
            name='error_count',
            field=models.PositiveIntegerField(editable=False, default=0),
        ),
        migrations.AddField(
            model_name='indicator',
            name='traceback',
            field=models.TextField(editable=False, blank=True),
        ),
    ]
