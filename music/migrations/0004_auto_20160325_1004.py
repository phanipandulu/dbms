# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-25 10:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0003_auto_20160325_1004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detail',
            name='id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='music.Login', unique=True),
        ),
    ]
