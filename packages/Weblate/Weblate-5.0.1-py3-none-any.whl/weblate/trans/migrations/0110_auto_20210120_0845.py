# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Generated by Django 3.1.4 on 2021-01-20 08:45

from django.db import migrations, models

import weblate.trans.fields


class Migration(migrations.Migration):
    dependencies = [
        ("trans", "0109_remove_project_mail"),
    ]

    operations = [
        migrations.AddField(
            model_name="variant",
            name="defining_units",
            field=models.ManyToManyField(
                related_name="defined_variants", to="trans.Unit"
            ),
        ),
        migrations.AlterField(
            model_name="variant",
            name="key",
            field=models.CharField(max_length=576),
        ),
        migrations.AlterField(
            model_name="variant",
            name="variant_regex",
            field=weblate.trans.fields.RegexField(blank=True, max_length=190),
        ),
    ]
