# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2018-07-19 16:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('screens', '0005_screenwidgetconfig'),
    ]

    operations = [
        migrations.AddField(
            model_name='screen',
            name='tag',
            field=models.TextField(default='aframe'),
        ),
    ]