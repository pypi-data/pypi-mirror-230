# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Generated by Django 3.0.7 on 2020-07-30 14:32

from django.db import migrations, models

import weblate.utils.validators


class Migration(migrations.Migration):
    dependencies = [
        ("trans", "0092_alert_dismissed"),
    ]

    operations = [
        migrations.AlterField(
            model_name="component",
            name="slug",
            field=models.SlugField(
                help_text="Name used in URLs and filenames.",
                max_length=100,
                validators=[weblate.utils.validators.validate_slug],
                verbose_name="URL slug",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="slug",
            field=models.SlugField(
                help_text="Name used in URLs and filenames.",
                max_length=60,
                unique=True,
                validators=[weblate.utils.validators.validate_slug],
                verbose_name="URL slug",
            ),
        ),
    ]
