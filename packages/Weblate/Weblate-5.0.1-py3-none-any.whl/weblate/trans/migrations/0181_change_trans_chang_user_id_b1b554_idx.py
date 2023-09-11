# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Generated by Django 4.2.3 on 2023-08-09 10:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("trans", "0180_change_duplicate_language"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="change",
            index=models.Index(
                fields=["user", "timestamp"], name="trans_chang_user_id_b1b554_idx"
            ),
        ),
    ]
