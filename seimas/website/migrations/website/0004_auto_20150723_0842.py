# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_auto_20150723_0701'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vote',
            old_name='position',
            new_name='vote',
        ),
    ]
