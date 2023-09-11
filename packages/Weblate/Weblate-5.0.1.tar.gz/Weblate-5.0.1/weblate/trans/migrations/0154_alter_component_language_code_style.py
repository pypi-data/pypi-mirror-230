# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Generated by Django 4.1b1 on 2022-07-18 13:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("trans", "0153_rename_java_language"),
    ]

    operations = [
        migrations.AlterField(
            model_name="component",
            name="language_code_style",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", "Default based on the file format"),
                    ("posix", "POSIX style using underscore as a separator"),
                    ("bcp", "BCP style using hyphen as a separator"),
                    (
                        "posix_long",
                        "POSIX style using underscore as a separator, including country code",
                    ),
                    (
                        "bcp_long",
                        "BCP style using hyphen as a separator, including country code",
                    ),
                    (
                        "bcp_legacy",
                        "BCP style using hyphen as a separator, legacy language codes",
                    ),
                    ("bcp_lower", "BCP style using hyphen as a separator, lower cased"),
                    ("android", "Android style"),
                    ("appstore", "App store metadata style"),
                    ("linux", "Linux style"),
                ],
                default="",
                help_text="Customize language code used to generate the filename for translations created by Weblate.",
                max_length=20,
                verbose_name="Language code style",
            ),
        ),
    ]
