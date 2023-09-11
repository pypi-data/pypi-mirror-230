# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Generated by Django 3.0.5 on 2020-04-16 11:21

import django.db.models.deletion
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import migrations, models


def create_index(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    if vendor == "postgresql":
        schema_editor.execute(
            "CREATE INDEX memory_source_fulltext ON memory_memory "
            "USING GIN (to_tsvector('english', source))"
        )
        schema_editor.execute(
            "CREATE INDEX memory_source_index ON memory_memory USING HASH (source)"
        )
        schema_editor.execute(
            "CREATE INDEX memory_target_index ON memory_memory USING HASH (target)"
        )
        schema_editor.execute(
            "CREATE INDEX memory_origin_index ON memory_memory USING HASH (origin)"
        )
    elif vendor == "mysql":
        schema_editor.execute(
            "CREATE FULLTEXT INDEX memory_source_fulltext ON memory_memory(source)"
        )
        schema_editor.execute(
            "CREATE INDEX memory_lookup_index ON "
            "memory_memory(source(255), target(255), origin(255))"
        )
    else:
        raise ImproperlyConfigured(f"Unsupported database: {vendor}")


def drop_index(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    if vendor == "postgresql":
        schema_editor.execute("DROP INDEX memory_source_fulltext")
        schema_editor.execute("DROP INDEX memory_source_index")
        schema_editor.execute("DROP INDEX memory_target_index")
        schema_editor.execute("DROP INDEX memory_origin_index")
    elif vendor == "mysql":
        schema_editor.execute(
            "ALTER TABLE memory_memory DROP INDEX memory_source_fulltext"
        )
        schema_editor.execute(
            "ALTER TABLE memory_memory DROP INDEX memory_lookup_index"
        )
    else:
        raise ImproperlyConfigured(f"Unsupported database: {vendor}")


class Migration(migrations.Migration):
    replaces = [
        ("memory", "0001_squashed_0003_auto_20180321_1554"),
        ("memory", "0002_memory"),
        ("memory", "0003_migrate_memory"),
        ("memory", "0004_memory_index"),
        ("memory", "0005_auto_20200310_0810"),
        ("memory", "0006_memory_update"),
    ]

    initial = True

    dependencies = [
        ("trans", "0063_auto_20200305_2202"),
        ("weblate_auth", "0006_auto_20190905_1139"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("lang", "0005_auto_20200212_1239"),
        ("lang", "0006_auto_20200309_1436"),
    ]

    operations = [
        migrations.CreateModel(
            name="Memory",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("source", models.TextField()),
                ("target", models.TextField()),
                ("origin", models.TextField()),
                ("from_file", models.BooleanField(db_index=True, default=False)),
                ("shared", models.BooleanField(db_index=True, default=False)),
                (
                    "project",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="trans.Project",
                    ),
                ),
                (
                    "source_language",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="memory_source_set",
                        to="lang.Language",
                    ),
                ),
                (
                    "target_language",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="memory_target_set",
                        to="lang.Language",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.RunPython(
            code=create_index,
            reverse_code=drop_index,
            atomic=False,
        ),
    ]
