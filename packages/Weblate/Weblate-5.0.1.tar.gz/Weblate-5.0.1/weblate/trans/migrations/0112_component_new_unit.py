# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Generated by Django 3.1.4 on 2021-01-27 14:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("trans", "0111_index_explanation"),
    ]

    operations = [
        migrations.AddField(
            model_name="component",
            name="new_unit",
            field=models.BooleanField(
                default=False,
                help_text="Disable adding new strings in Weblate in case the strings are automatically extracted from the source.",
                verbose_name="Adding new strings",
            ),
        ),
    ]
