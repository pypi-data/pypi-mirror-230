# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Generated by Django 4.2.3 on 2023-08-04 10:42

from django.db import migrations

from weblate.utils.fields import migrate_json_field


def addons_jsonfield(apps, schema_editor):
    migrate_json_field(
        apps.get_model("addons", "Addon"), schema_editor.connection.alias, "state"
    )
    migrate_json_field(
        apps.get_model("addons", "Addon"),
        schema_editor.connection.alias,
        "configuration",
    )


class Migration(migrations.Migration):
    dependencies = [
        ("addons", "0004_addon_configuration_new_addon_state_new"),
    ]

    operations = [migrations.RunPython(addons_jsonfield, elidable=True)]
