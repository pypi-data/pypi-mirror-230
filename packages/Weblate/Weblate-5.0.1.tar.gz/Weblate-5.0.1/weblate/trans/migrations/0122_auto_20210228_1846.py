# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Generated by Django 3.1.4 on 2021-02-28 17:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("trans", "0121_remove_component_glossary_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="variant",
            name="key",
            field=models.CharField(max_length=576),
        ),
    ]
