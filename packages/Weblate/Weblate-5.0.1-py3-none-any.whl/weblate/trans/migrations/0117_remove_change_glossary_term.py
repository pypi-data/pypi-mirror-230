# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Generated by Django 3.1.4 on 2021-02-03 13:42

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("trans", "0116_migrate_glossaries"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="change",
            name="glossary_term",
        ),
    ]
