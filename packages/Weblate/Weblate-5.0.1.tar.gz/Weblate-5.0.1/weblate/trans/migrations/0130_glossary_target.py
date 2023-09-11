# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Generated by Django 3.1.7 on 2021-03-24 14:39

from django.db import migrations
from django.db.models import F


def glossary_target(apps, schema_editor):
    Unit = apps.get_model("trans", "Unit")
    db_alias = schema_editor.connection.alias
    Unit.objects.using(db_alias).filter(
        translation__component__is_glossary=True,
        translation__language=F("translation__component__source_language"),
    ).exclude(source=F("target")).update(target=F("source"))


class Migration(migrations.Migration):
    dependencies = [
        ("trans", "0129_auto_20210319_1419"),
    ]

    operations = [
        migrations.RunPython(glossary_target, migrations.RunPython.noop, elidable=True),
    ]
