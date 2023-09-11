# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Generated by Django 3.2 on 2021-05-12 19:55

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("memory", "0010_auto_20210506_1439"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="memory",
            options={
                "verbose_name": "Translation memory entry",
                "verbose_name_plural": "Translation memory entries",
            },
        ),
    ]
