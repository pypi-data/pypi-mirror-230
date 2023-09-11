# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Generated by Django 4.1.7 on 2023-03-14 11:28

from django.db import migrations


def remove_blank(apps, schema_editor):
    Memory = apps.get_model("memory", "Memory")
    Memory.objects.using(schema_editor.connection.alias).filter(source="").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("memory", "0014_rename_index"),
    ]

    operations = [migrations.RunPython(remove_blank, elidable=True)]
