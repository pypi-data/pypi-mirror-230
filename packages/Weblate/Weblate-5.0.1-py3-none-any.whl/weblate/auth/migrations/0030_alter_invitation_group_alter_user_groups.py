# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Generated by Django 4.2.3 on 2023-08-21 11:31

import django.db.models.deletion
from django.db import migrations, models

import weblate.auth.models


class Migration(migrations.Migration):
    dependencies = [
        ("weblate_auth", "0029_invitation"),
    ]

    operations = [
        migrations.AlterField(
            model_name="invitation",
            name="group",
            field=models.ForeignKey(
                help_text="The user is granted all permissions included in membership of these teams.",
                on_delete=django.db.models.deletion.CASCADE,
                to="weblate_auth.group",
                verbose_name="Team",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="groups",
            field=weblate.auth.models.GroupManyToManyField(
                blank=True,
                help_text="The user is granted all permissions included in membership of these teams.",
                to="weblate_auth.group",
                verbose_name="Teams",
            ),
        ),
    ]
