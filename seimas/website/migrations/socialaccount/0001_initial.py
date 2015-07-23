# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import allauth.socialaccount.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialAccount',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('provider', models.CharField(choices=[('persona', 'Persona'), ('github', 'GitHub'), ('openid', 'OpenID'), ('facebook', 'Facebook'), ('twitter', 'Twitter'), ('google', 'Google'), ('linkedin', 'LinkedIn')], max_length=30, verbose_name='provider')),
                ('uid', models.CharField(verbose_name='uid', max_length=255)),
                ('last_login', models.DateTimeField(verbose_name='last login', auto_now=True)),
                ('date_joined', models.DateTimeField(verbose_name='date joined', auto_now_add=True)),
                ('extra_data', allauth.socialaccount.fields.JSONField(default='{}', verbose_name='extra data')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'social account',
                'verbose_name_plural': 'social accounts',
            },
        ),
        migrations.CreateModel(
            name='SocialApp',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('provider', models.CharField(choices=[('persona', 'Persona'), ('github', 'GitHub'), ('openid', 'OpenID'), ('facebook', 'Facebook'), ('twitter', 'Twitter'), ('google', 'Google'), ('linkedin', 'LinkedIn')], max_length=30, verbose_name='provider')),
                ('name', models.CharField(verbose_name='name', max_length=40)),
                ('client_id', models.CharField(verbose_name='client id', max_length=100, help_text='App ID, or consumer key')),
                ('secret', models.CharField(verbose_name='secret key', max_length=100, help_text='API secret, client secret, or consumer secret')),
                ('key', models.CharField(verbose_name='key', max_length=100, help_text='Key', blank=True)),
                ('sites', models.ManyToManyField(to='sites.Site', blank=True)),
            ],
            options={
                'verbose_name': 'social application',
                'verbose_name_plural': 'social applications',
            },
        ),
        migrations.CreateModel(
            name='SocialToken',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('token', models.TextField(verbose_name='social account', help_text='"oauth_token" (OAuth1) or access token (OAuth2)')),
                ('token_secret', models.TextField(verbose_name='token secret', help_text='"oauth_token_secret" (OAuth1) or refresh token (OAuth2)', blank=True)),
                ('expires_at', models.DateTimeField(verbose_name='expires at', null=True, blank=True)),
                ('account', models.ForeignKey(to='socialaccount.SocialAccount')),
                ('app', models.ForeignKey(to='socialaccount.SocialApp')),
            ],
            options={
                'verbose_name': 'social application token',
                'verbose_name_plural': 'social application tokens',
            },
        ),
        migrations.AlterUniqueTogether(
            name='socialtoken',
            unique_together=set([('app', 'account')]),
        ),
        migrations.AlterUniqueTogether(
            name='socialaccount',
            unique_together=set([('provider', 'uid')]),
        ),
    ]
