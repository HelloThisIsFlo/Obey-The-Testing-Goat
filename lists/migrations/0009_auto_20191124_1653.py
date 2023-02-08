# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2019-11-24 16:53
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lists', '0008_list_sharees'),
    ]

    operations = [
        migrations.AlterField(
            model_name='list',
            name='sharees',
            field=models.ManyToManyField(related_name='shared_lists', to=settings.AUTH_USER_MODEL),
        ),
    ]