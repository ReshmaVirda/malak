# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-07-13 12:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Account', '0011_auto_20220713_1806'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='created_at',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='modified_at',
            field=models.DateField(),
        ),
    ]
