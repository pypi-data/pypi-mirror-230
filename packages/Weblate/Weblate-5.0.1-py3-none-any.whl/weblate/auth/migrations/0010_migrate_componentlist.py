# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Generated by Django 3.0.7 on 2020-06-11 19:33

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("weblate_auth", "0009_migrate_componentlist"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="group",
            name="componentlist",
        ),
    ]
