# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-26 10:14
from __future__ import unicode_literals

from django.db import migrations
from manopozicija.migrations import LoadExtension


class Migration(migrations.Migration):

    dependencies = [
        ('manopozicija', '0005_auto_20160725_1021'),
    ]

    operations = [
        LoadExtension('pg_trgm'),
    ]