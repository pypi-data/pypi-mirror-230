# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Generated by Django 4.0.1 on 2022-01-26 11:52

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("weblate_auth", "0021_migrate_internal_groups"),
    ]

    operations = [
        migrations.AlterModelManagers(
            name="user",
            managers=[],
        ),
    ]
