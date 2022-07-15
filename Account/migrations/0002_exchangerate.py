# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-07-05 12:09
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Exchangerate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency_name', models.CharField(max_length=255)),
                ('is_default', models.BooleanField(default=False)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('modified_at', models.DateField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='currency', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
