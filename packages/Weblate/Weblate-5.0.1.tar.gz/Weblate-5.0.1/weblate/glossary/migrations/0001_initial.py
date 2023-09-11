# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Generated by Django 3.0.6 on 2020-06-09 09:12

import django.db.models.deletion
from django.db import migrations, models

from weblate.trans.defines import PROJECT_NAME_LENGTH

GLOSSARY_LENGTH = 190


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("lang", "0009_auto_20200521_0753"),
        ("trans", "0084_auto_20200605_0648"),
    ]

    operations = [
        migrations.CreateModel(
            name="Glossary",
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
                (
                    "name",
                    models.CharField(
                        max_length=PROJECT_NAME_LENGTH,
                        unique=True,
                        verbose_name="Glossary name",
                    ),
                ),
                (
                    "color",
                    models.CharField(
                        choices=[
                            ("navy", "Navy"),
                            ("blue", "Blue"),
                            ("aqua", "Aqua"),
                            ("teal", "Teal"),
                            ("olive", "Olive"),
                            ("green", "Green"),
                            ("lime", "Lime"),
                            ("yellow", "Yellow"),
                            ("orange", "Orange"),
                            ("red", "Red"),
                            ("maroon", "Maroon"),
                            ("fuchsia", "Fuchsia"),
                            ("purple", "Purple"),
                            ("black", "Black"),
                            ("gray", "Gray"),
                            ("silver", "Silver"),
                        ],
                        default=None,
                        max_length=30,
                        verbose_name="Color",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="trans.Project"
                    ),
                ),
                (
                    "links",
                    models.ManyToManyField(
                        blank=True,
                        to="trans.Project",
                        verbose_name="Additional projects",
                        related_name="linked_glossaries",
                        help_text="Choose additional projects where this glossary can be used.",
                    ),
                ),
            ],
            options={"verbose_name": "glossary", "verbose_name_plural": "glossaries"},
        ),
        migrations.CreateModel(
            name="Term",
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
                (
                    "source",
                    models.CharField(
                        db_index=True, max_length=GLOSSARY_LENGTH, verbose_name="Source"
                    ),
                ),
                (
                    "target",
                    models.CharField(
                        max_length=GLOSSARY_LENGTH, verbose_name="Translation"
                    ),
                ),
                (
                    "glossary",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="glossary.Glossary",
                        verbose_name="Glossary",
                    ),
                ),
                (
                    "language",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="lang.Language"
                    ),
                ),
            ],
            options={
                "verbose_name": "glossary term",
                "verbose_name_plural": "glossary terms",
            },
        ),
    ]
