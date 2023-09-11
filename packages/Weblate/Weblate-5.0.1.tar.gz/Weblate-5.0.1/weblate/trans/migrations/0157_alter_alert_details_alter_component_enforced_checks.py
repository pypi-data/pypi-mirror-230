# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Generated by Django 4.1 on 2022-09-15 11:00

from django.db import migrations

import weblate.utils.fields


class Migration(migrations.Migration):
    dependencies = [
        ("trans", "0156_alter_change_action"),
    ]

    operations = [
        migrations.AlterField(
            model_name="alert",
            name="details",
            field=weblate.utils.fields.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name="component",
            name="enforced_checks",
            field=weblate.utils.fields.JSONField(
                blank=True,
                default=list,
                help_text="List of checks which can not be ignored.",
                verbose_name="Enforced checks",
            ),
        ),
    ]
