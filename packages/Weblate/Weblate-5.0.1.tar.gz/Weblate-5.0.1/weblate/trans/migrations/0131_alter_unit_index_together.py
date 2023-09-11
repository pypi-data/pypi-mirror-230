# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Generated by Django 3.2 on 2021-05-06 14:27

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("trans", "0130_glossary_target"),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name="unit",
            index_together=set(),
        ),
    ]
