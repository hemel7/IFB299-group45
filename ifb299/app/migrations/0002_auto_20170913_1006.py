# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-09-13 00:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('STUDENT', 'STUDENT'), ('BUSINESSMAN', 'BUSINESSMAN'), ('TOURIST', 'TOURIST')], max_length=20),
        ),
    ]
