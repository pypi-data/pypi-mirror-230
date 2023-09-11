# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Generated by Django 4.2.3 on 2023-09-05 12:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("trans", "0187_alter_variant_unique_together_alter_alert_component_and_more"),
        ("fonts", "0002_auto_20210512_1955"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="fontgroup",
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name="fontgroup",
            name="project",
            field=models.ForeignKey(
                db_index=False,
                on_delete=django.db.models.deletion.CASCADE,
                to="trans.project",
            ),
        ),
        migrations.AlterField(
            model_name="fontoverride",
            name="group",
            field=models.ForeignKey(
                db_index=False,
                on_delete=django.db.models.deletion.CASCADE,
                to="fonts.fontgroup",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="fontgroup",
            unique_together={("project", "name")},
        ),
    ]
