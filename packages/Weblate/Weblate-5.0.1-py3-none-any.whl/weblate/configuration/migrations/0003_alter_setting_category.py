# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Generated by Django 4.0.4 on 2022-05-12 11:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("configuration", "0002_alter_setting_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="setting",
            name="category",
            field=models.IntegerField(choices=[(1, "UI"), (2, "MT")], db_index=True),
        ),
    ]
