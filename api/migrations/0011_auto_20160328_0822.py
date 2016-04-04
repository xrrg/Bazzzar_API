# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-28 08:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_auto_20160328_0753'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advertisement',
            name='clothes_sex',
            field=models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='advertisement',
            name='condition',
            field=models.BooleanField(help_text='Check - New thing, None - Used thing'),
        ),
        migrations.AlterField(
            model_name='housing',
            name='area',
            field=models.DecimalField(decimal_places=2, max_digits=5),
        ),
        migrations.AlterField(
            model_name='kidsthings',
            name='age',
            field=models.PositiveSmallIntegerField(),
        ),
        migrations.AlterField(
            model_name='kidsthings',
            name='sex',
            field=models.BooleanField(help_text='Check - for boy , None - for girl'),
        ),
        migrations.AlterField(
            model_name='transport',
            name='motor_power',
            field=models.PositiveSmallIntegerField(),
        ),
    ]