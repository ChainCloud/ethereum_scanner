# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-19 08:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_follows', '0002_ethaccountinfo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='follow',
            name='address',
            field=models.CharField(db_index=True, max_length=63),
        ),
    ]
