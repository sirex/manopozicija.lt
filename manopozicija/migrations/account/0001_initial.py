# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailAddress',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('email', models.EmailField(verbose_name='e-mail address', unique=True, max_length=254)),
                ('verified', models.BooleanField(default=False, verbose_name='verified')),
                ('primary', models.BooleanField(default=False, verbose_name='primary')),
                ('user', models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'email addresses',
                'verbose_name': 'email address',
            },
        ),
        migrations.CreateModel(
            name='EmailConfirmation',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created')),
                ('sent', models.DateTimeField(verbose_name='sent', null=True)),
                ('key', models.CharField(verbose_name='key', unique=True, max_length=64)),
                ('email_address', models.ForeignKey(verbose_name='e-mail address', to='account.EmailAddress')),
            ],
            options={
                'verbose_name_plural': 'email confirmations',
                'verbose_name': 'email confirmation',
            },
        ),
    ]
