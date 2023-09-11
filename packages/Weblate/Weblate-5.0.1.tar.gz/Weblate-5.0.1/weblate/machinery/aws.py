# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import boto3
from django.conf import settings
from django.utils.functional import cached_property

from .base import MachineTranslation
from .forms import AWSMachineryForm


class AWSTranslation(MachineTranslation):
    """AWS machine translation."""

    name = "AWS"
    max_score = 88
    language_map = {
        "zh_Hant": "zh-TW",
        "zh_Hans": "zh",
    }
    settings_form = AWSMachineryForm

    @cached_property
    def client(self):
        return boto3.client(
            "translate",
            region_name=self.settings["region"],
            aws_access_key_id=self.settings["key"],
            aws_secret_access_key=self.settings["secret"],
        )

    @staticmethod
    def migrate_settings():
        return {
            "region": settings.MT_AWS_REGION,
            "key": settings.MT_AWS_ACCESS_KEY_ID,
            "secret": settings.MT_AWS_SECRET_ACCESS_KEY,
        }

    def map_language_code(self, code):
        """Convert language to service specific code."""
        return super().map_language_code(code).replace("_", "-").split("@")[0]

    def download_languages(self):
        """
        Hardcoded list of supported languages as there is no API to get this.

        Can be generated by HTML scraping using
        ./scripts/generate-aws-languages
        """
        return (
            "af",
            "am",
            "ar",
            "az",
            "bg",
            "bn",
            "bs",
            "ca",
            "cs",
            "cy",
            "da",
            "de",
            "el",
            "en",
            "es",
            "es-MX",
            "et",
            "fa",
            "fa-AF",
            "fi",
            "fr",
            "fr-CA",
            "gu",
            "ha",
            "he",
            "hi",
            "hr",
            "ht",
            "hu",
            "hy",
            "id",
            "is",
            "it",
            "ja",
            "ka",
            "kk",
            "kn",
            "ko",
            "lt",
            "lv",
            "mk",
            "ml",
            "mn",
            "ms",
            "mt",
            "nl",
            "no",
            "pl",
            "ps",
            "pt",
            "ro",
            "ru",
            "si",
            "sk",
            "sl",
            "so",
            "sq",
            "sr",
            "sv",
            "sw",
            "ta",
            "te",
            "th",
            "tl",
            "tr",
            "uk",
            "ur",
            "uz",
            "vi",
            "zh",
            "zh-TW",
        )

    def download_translations(
        self,
        source,
        language,
        text: str,
        unit,
        user,
        threshold: int = 75,
    ):
        response = self.client.translate_text(
            Text=text, SourceLanguageCode=source, TargetLanguageCode=language
        )
        yield {
            "text": response["TranslatedText"],
            "quality": self.max_score,
            "service": self.name,
            "source": text,
        }
