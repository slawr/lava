# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-08 17:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lava_scheduler_app', '0035_remove_testjob__results_link'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='device',
            name='is_pipeline',
        ),
        migrations.RemoveField(
            model_name='testjob',
            name='is_pipeline',
        ),
    ]
