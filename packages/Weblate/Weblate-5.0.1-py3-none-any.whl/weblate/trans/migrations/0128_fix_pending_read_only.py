# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Generated by Django 3.1.7 on 2021-03-17 07:15

from django.db import migrations
from django.db.models import F


def fixup_readonly(apps, schema_editor):
    Translation = apps.get_model("trans", "Translation")
    db_alias = schema_editor.connection.alias
    for translation in Translation.objects.using(db_alias).filter(
        component__template="",
        language_id=F("component__source_language_id"),
        check_flags="",
    ):
        translation.check_flags = "read-only"
        translation.save(update_fields=["check_flags"])
        translation.unit_set.filter(pending=True).update(pending=False)


class Migration(migrations.Migration):
    dependencies = [
        ("trans", "0127_fix_source_glossary"),
    ]

    operations = [
        migrations.RunPython(fixup_readonly, migrations.RunPython.noop, elidable=True)
    ]
