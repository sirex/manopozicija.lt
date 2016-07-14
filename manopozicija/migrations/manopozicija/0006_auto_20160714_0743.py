# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-14 07:43
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('manopozicija', '0005_auto_20160714_0330'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('action', models.PositiveSmallIntegerField(choices=[(1, 'balsavo')])),
                ('vote', models.SmallIntegerField(blank=True, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='curatorapproval',
            name='item',
        ),
        migrations.RemoveField(
            model_name='curatorapproval',
            name='user',
        ),
        migrations.AlterUniqueTogether(
            name='curatorqueueitem',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='curatorqueueitem',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='curatorqueueitem',
            name='topic',
        ),
        migrations.RemoveField(
            model_name='post',
            name='approved',
        ),
        migrations.AddField(
            model_name='post',
            name='approved',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.DeleteModel(
            name='CuratorApproval',
        ),
        migrations.DeleteModel(
            name='CuratorQueueItem',
        ),
        migrations.AddField(
            model_name='postlog',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manopozicija.Post'),
        ),
        migrations.AddField(
            model_name='postlog',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]