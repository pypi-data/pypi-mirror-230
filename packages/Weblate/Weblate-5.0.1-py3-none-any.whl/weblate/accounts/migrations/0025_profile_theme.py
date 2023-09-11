# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Generated by Django 4.2.1 on 2023-06-08 12:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0024_rename_be_latn"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="theme",
            field=models.CharField(
                choices=[
                    ("auto", "Sync with system"),
                    ("light", "Light"),
                    ("dark", "Dark"),
                ],
                default="auto",
                max_length=10,
                verbose_name="Theme",
            ),
        ),
    ]
