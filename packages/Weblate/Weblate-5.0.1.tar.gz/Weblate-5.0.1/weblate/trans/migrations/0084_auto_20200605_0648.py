# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Generated by Django 3.0.6 on 2020-06-05 06:48

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("trans", "0083_component_restricted"),
    ]

    operations = [
        migrations.RenameField(
            model_name="unit",
            old_name="extra_context",
            new_name="explanation",
        ),
    ]
