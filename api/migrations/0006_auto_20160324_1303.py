# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-24 13:03
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20160324_1251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advertisement',
            name='phone',
            field=models.CharField(max_length=100, validators=[django.core.validators.RegexValidator(inverse_match=True, message='Enter correct phone number', regex='[^0-9$]')]),
        ),
    ]
