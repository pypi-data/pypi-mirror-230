#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import platform
from logging.handlers import SysLogHandler

# Title of site to use
SITE_TITLE = "Weblate"

# Site domain
SITE_DOMAIN = "127.0.0.1:8000"

# Whether to offer hosting
OFFER_HOSTING = False
OFFER_HOSTING = True

# Whether site uses https
ENABLE_HTTPS = False

#
# Django settings for Weblate project.
#

DEBUG = False
DEBUG = True

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
    ("Michal Cihar", "michal@cihar.com"),
)

MANAGERS = ADMINS

DATABASES = {
    "default": {
        # Use "postgresql" or "mysql".
        "ENGINE": "django.db.backends.postgresql",
        # Database name.
        "NAME": "weblate",
        # Database user.
        "USER": "weblate",
        # Name of role to alter to set parameters in PostgreSQL,
        # use in case role name is different than user used for authentication.
        # "ALTER_ROLE": "weblate",
        # Database password.
        "PASSWORD": "weblate",
        # Set to empty string for localhost.
        "HOST": "127.0.0.1",
        # Set to empty string for default.
        "PORT": "",
        # Customizations for databases.
        "OPTIONS": {
            # In case of using an older MySQL server,
            # which has MyISAM as a default storage
            # "init_command": "SET storage_engine=INNODB",
            # Uncomment for MySQL older than 5.7:
            # "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            # Set emoji capable charset for MySQL:
            # "charset": "utf8mb4",
            # Change connection timeout in case you get MySQL gone away error:
            # "connect_timeout": 28800,
        },
        # Persistent connections
        "CONN_MAX_AGE": 0,
        # Disable server-side cursors, might be needed with pgbouncer
        "DISABLE_SERVER_SIDE_CURSORS": False,
    },
    "payments_db": {
        # Use 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        "ENGINE": "django.db.backends.sqlite3",
        # Database name or path to database file if using sqlite3.
        "NAME": "/home/nijel/weblate/hosted/payments.db",
    },
}
DATABASES["memory_db"] = DATABASES["default"]

DATABASE_ROUTERS = ["wlhosted.dbrouter.HostedRouter"]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Data directory
DATA_DIR = os.path.join(BASE_DIR, "data")

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = "Europe/Prague"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"

LANGUAGES = (
    ("ar", "العربية"),
    ("az", "Azərbaycan"),
    ("be", "Беларуская"),
    ("be@latin", "Biełaruskaja"),
    ("bg", "Български"),
    ("br", "Brezhoneg"),
    ("ca", "Català"),
    ("cs", "Čeština"),
    ("da", "Dansk"),
    ("de", "Deutsch"),
    ("en", "English"),
    ("el", "Ελληνικά"),
    ("en-gb", "English (United Kingdom)"),
    ("es", "Español"),
    ("fi", "Suomi"),
    ("fr", "Français"),
    ("gl", "Galego"),
    ("he", "עברית"),
    ("hu", "Magyar"),
    ("hr", "Hrvatski"),
    ("id", "Indonesia"),
    ("is", "Íslenska"),
    ("it", "Italiano"),
    ("ja", "日本語"),
    ("kab", "Taqbaylit"),
    ("kk", "Қазақ тілі"),
    ("ko", "한국어"),
    ("nb", "Norsk bokmål"),
    ("nl", "Nederlands"),
    ("pl", "Polski"),
    ("pt", "Português"),
    ("pt-br", "Português brasileiro"),
    ("ro", "Română"),
    ("ru", "Русский"),
    ("sk", "Slovenčina"),
    ("sl", "Slovenščina"),
    ("sq", "Shqip"),
    ("sr", "Српски"),
    ("sr-latn", "Srpski"),
    ("sv", "Svenska"),
    ("th", "ไทย"),
    ("tr", "Türkçe"),
    ("uk", "Українська"),
    ("zh-hans", "简体中文"),
    ("zh-hant", "正體中文"),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Type of automatic primary key, introduced in Django 3.2
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# URL prefix to use, please see documentation for more details
URL_PREFIX = ""

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = os.path.join(DATA_DIR, "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
MEDIA_URL = f"{URL_PREFIX}/media/"

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
STATIC_ROOT = os.path.join(DATA_DIR, "static")

# URL prefix for static files.
STATIC_URL = f"{URL_PREFIX}/static/"

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
)

# Make this unique, and don't share it with anybody.
# You can generate it using weblate-generate-secret-key
SECRET_KEY = "jm8fqjlg+5!#xu%e-oh#7!$aa7!6avf7ud*_v=chdrb9qdco6("

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.request",
                "django.template.context_processors.csrf",
                "django.contrib.messages.context_processors.messages",
                "weblate.trans.context_processors.weblate_context",
            ],
        },
        "APP_DIRS": True
    }
]


# GitHub username and token for sending pull requests.
# Please see the documentation for more details.
GITHUB_CREDENTIALS = {}

# GitLab username and token for sending merge requests.
# Please see the documentation for more details.
GITLAB_CREDENTIALS = {}

PAGURE_CREDENTIALS = {
    "pagure.io": {
        "username": "nijel",
        "token": "ZU5V2DWWUC28WLC72ZLJDNP9SKOXT78U0PL0TSR37KRC83EXZO51YKINJ4NVY6VS",
    }
}

# Authentication configuration
AUTHENTICATION_BACKENDS = (
    "social_core.backends.email.EmailAuth",
    "social_core.backends.username.UsernameAuth",
    "social_core.backends.google.GoogleOAuth2",
    "social_core.backends.github.GithubOAuth2",
    "social_core.backends.gitlab.GitLabOAuth2",
    "social_core.backends.bitbucket.BitbucketOAuth",
    "social_core.backends.suse.OpenSUSEOpenId",
    "social_core.backends.ubuntu.UbuntuOpenId",
    "social_core.backends.fedora.FedoraOpenId",
    "social_core.backends.facebook.FacebookOAuth2",
    "social_core.backends.auth0.Auth0OAuth2",
    "social_core.backends.amazon.AmazonOAuth2",
    "social_core.backends.saml.SAMLAuth",
    "weblate.accounts.auth.WeblateUserBackend",
)

# Custom user model
AUTH_USER_MODEL = "weblate_auth.User"

# Social auth backends setup
SOCIAL_AUTH_GITHUB_KEY = "7eb4db301a3fc9df0caa"
SOCIAL_AUTH_GITHUB_SECRET = "431b3d1a45e8a61b6fe7055d85b249e1fcc76794" # DONE
SOCIAL_AUTH_GITHUB_SCOPE = ["user:email"]

SOCIAL_AUTH_BITBUCKET_KEY = ""
SOCIAL_AUTH_BITBUCKET_SECRET = ""
SOCIAL_AUTH_BITBUCKET_VERIFIED_EMAILS_ONLY = True

SOCIAL_AUTH_FACEBOOK_KEY = ""
SOCIAL_AUTH_FACEBOOK_SECRET = ""
SOCIAL_AUTH_FACEBOOK_SCOPE = ["email", "public_profile"]
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {"fields": "id,name,email"}

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = (
    "851612429544-86vqa17ep73jk237796uditmnd1n9uq2.apps.googleusercontent.com" # DONE
)
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = "FFhlgnXwqnQN64n8iMNu8gkP"

SOCIAL_AUTH_AUTH0_DOMAIN = "dev-iv1n0jtx.auth0.com"
SOCIAL_AUTH_AUTH0_KEY = "7YMNPNqWygO86JUIC1ksSkiIJ9TpSu0t" # TODO, probably discarded
SOCIAL_AUTH_AUTH0_SECRET = (
    "NgnCqFXB0vUHqZAp4u1T7s1guPeF_SRzMj5zGWUQQMDdOs6Q6WozK2vq6j810IuR"
)
SOCIAL_AUTH_AUTH0_SCOPE = ["openid", "profile", "email"]

# Social auth settings
SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "weblate.accounts.pipeline.store_params",
    "weblate.accounts.pipeline.verify_open",
    "social_core.pipeline.user.get_username",
    "weblate.accounts.pipeline.require_email",
    "social_core.pipeline.mail.mail_validation",
    "weblate.accounts.pipeline.revoke_mail_code",
    "weblate.accounts.pipeline.ensure_valid",
    "weblate.accounts.pipeline.remove_account",
    "social_core.pipeline.social_auth.associate_by_email",
    "weblate.accounts.pipeline.reauthenticate",
    "weblate.accounts.pipeline.verify_username",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "weblate.legal.pipeline.tos_confirm",
    "weblate.accounts.pipeline.cleanup_next",
    "weblate.accounts.pipeline.user_full_name",
    "weblate.accounts.pipeline.store_email",
    "weblate.accounts.pipeline.notify_connect",
    "weblate.accounts.pipeline.handle_invite",
    "weblate.accounts.pipeline.password_reset",
)
SOCIAL_AUTH_DISCONNECT_PIPELINE = (
    "social_core.pipeline.disconnect.allowed_to_disconnect",
    "social_core.pipeline.disconnect.get_entries",
    "social_core.pipeline.disconnect.revoke_tokens",
    "weblate.accounts.pipeline.cycle_session",
    "weblate.accounts.pipeline.adjust_primary_mail",
    "weblate.accounts.pipeline.notify_disconnect",
    "social_core.pipeline.disconnect.disconnect",
    "weblate.accounts.pipeline.cleanup_next",
)

# Custom authentication strategy
SOCIAL_AUTH_STRATEGY = "weblate.accounts.strategy.WeblateStrategy"

# Raise exceptions so that we can handle them later
SOCIAL_AUTH_RAISE_EXCEPTIONS = True

SOCIAL_AUTH_EMAIL_VALIDATION_FUNCTION = "weblate.accounts.pipeline.send_validation"
SOCIAL_AUTH_EMAIL_VALIDATION_URL = f"{URL_PREFIX}/accounts/email-sent/"
SOCIAL_AUTH_LOGIN_ERROR_URL = f"{URL_PREFIX}/accounts/login/"
SOCIAL_AUTH_EMAIL_FORM_URL = f"{URL_PREFIX}/accounts/email/"
SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = f"{URL_PREFIX}/accounts/profile/#account"
SOCIAL_AUTH_PROTECTED_USER_FIELDS = ("email",)
SOCIAL_AUTH_SLUGIFY_USERNAMES = True
SOCIAL_AUTH_SLUGIFY_FUNCTION = "weblate.accounts.pipeline.slugify_username"

# Password validation configuration
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "weblate.accounts.password_validation.CharsPasswordValidator"},
    # Optional password strength validation by django-zxcvbn-password
    # {
    #     "NAME": "zxcvbn_password.ZXCVBNValidator",
    #     "OPTIONS": {
    #         "min_score": 3,
    #         "user_attributes": ("username", "email", "full_name")
    #     }
    # },
]

# Password hashing (prefer Argon)
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

# Allow new user registrations
REGISTRATION_OPEN = True

# Shortcut for login required setting
REQUIRE_LOGIN = False

# Middleware
MIDDLEWARE = [
    "weblate.middleware.RedirectMiddleware",
    "weblate.middleware.ProxyMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "weblate.accounts.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
    "weblate.accounts.middleware.RequireLoginMiddleware",
    "weblate.api.middleware.ThrottlingMiddleware",
    "weblate.middleware.SecurityMiddleware",
    "weblate.wladmin.middleware.ManageMiddleware",
    "weblate.legal.middleware.RequireTOSMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = "weblate.urls"

# Django and Weblate apps
INSTALLED_APPS = [
    # Weblate apps on top to override Django locales and templates
    "weblate.addons",
    "weblate.auth",
    "weblate.checks",
    "weblate.formats",
    "weblate.glossary",
    "weblate.machinery",
    "weblate.trans",
    "weblate.lang",
    "weblate_language_data",
    "weblate.memory",
    "weblate.screenshots",
    "weblate.fonts",
    "weblate.accounts",
    "weblate.configuration",
    "weblate.utils",
    "weblate.vcs",
    "weblate.wladmin",
    "weblate.metrics",
    "weblate",
    # Optional: Git exporter
    "weblate.gitexport",
    "wllegal",
    "wlhosted",
    "wlhosted.payments",
    "wlhosted.integrations",
    "weblate.legal",
    "weblate.billing",
    "debug_toolbar",
    # Standard Django modules
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin.apps.SimpleAdminConfig",
    "django.contrib.admindocs",
    "django.contrib.sitemaps",
    "django.contrib.humanize",
    # Third party Django modules
    "social_django",
    "crispy_forms",
    "crispy_bootstrap3",
    "compressor",
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "django_celery_beat",
    "djangosaml2idp",
]

# Custom exception reporter to include some details
DEFAULT_EXCEPTION_REPORTER_FILTER = "weblate.trans.debug.WeblateExceptionReporterFilter"

# Default logging of Weblate messages
# - to syslog in production (if available)
# - otherwise to console
# - you can also choose "logfile" to log into separate file
#   after configuring it below

# Detect if we can connect to syslog
HAVE_SYSLOG = False
if platform.system() != "Windows":
    try:
        handler = SysLogHandler(address="/dev/log", facility=SysLogHandler.LOG_LOCAL2)
        handler.close()
        HAVE_SYSLOG = True
    except OSError:
        HAVE_SYSLOG = False

if DEBUG or not HAVE_SYSLOG:
    DEFAULT_LOG = "console"
else:
    DEFAULT_LOG = "syslog"
DEFAULT_LOGLEVEL = "DEBUG" if DEBUG else "INFO"

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/stable/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {
        #        'django.server': {
        #            '()': 'django.utils.log.ServerFormatter',
        #            'format': '[%(server_time)s] %(message)s',
        #        },
        "syslog": {"format": "weblate[%(process)d]: %(levelname)s %(message)s"},
        "simple": {"format": "[%(asctime)s: %(levelname)s/%(process)s] %(message)s"},
        "logfile": {"format": "%(asctime)s %(levelname)s %(message)s"},
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[%(server_time)s] %(message)s",
        },
    },
    "handlers": {
        #        'django.server': {
        #            'level': 'INFO',
        #            'class': 'logging.StreamHandler',
        #            'formatter': 'django.server',
        #        },
        "django.template": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
            "include_html": True,
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        "syslog": {
            "level": "DEBUG",
            "class": "logging.handlers.SysLogHandler",
            "formatter": "syslog",
            "address": "/dev/log",
            "facility": SysLogHandler.LOG_LOCAL2,
        },
        # Logging to a file
        # "logfile": {
        #     "level":"DEBUG",
        #     "class":"logging.handlers.RotatingFileHandler",
        #     "filename": "/var/log/weblate/weblate.log",
        #     "maxBytes": 100000,
        #     "backupCount": 3,
        #     "formatter": "logfile",
        # },
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins", DEFAULT_LOG],
            "level": "ERROR",
            "propagate": True,
        },
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        },
        # Logging database queries
        #"django.db.backends": {
        #    "handlers": [DEFAULT_LOG],
        #    "level": "DEBUG",
        #},
        "redis_lock": {"handlers": [DEFAULT_LOG], "level": "DEBUG"},
        "weblate": {"handlers": [DEFAULT_LOG], "level": DEFAULT_LOGLEVEL},
        # Logging VCS operations
        "weblate.vcs": {"handlers": [DEFAULT_LOG], "level": DEFAULT_LOGLEVEL},
        # Python Social Auth
        "social": {"handlers": [DEFAULT_LOG], "level": DEFAULT_LOGLEVEL},
        # Django Authentication Using LDAP
        "django_auth_ldap": {"handlers": [DEFAULT_LOG], "level": DEFAULT_LOGLEVEL},
        # SAML IdP
        "djangosaml2idp": {"handlers": [DEFAULT_LOG], "level": DEFAULT_LOGLEVEL},
    },
}

# Remove syslog setup if it's not present
if not HAVE_SYSLOG:
    del LOGGING["handlers"]["syslog"]

# List of machine translations
MT_SERVICES = (
    #     "weblate.machinery.apertium.ApertiumAPYTranslation",
    #"weblate.machinery.baidu.BaiduTranslation",
    "weblate.machinery.deepl.DeepLTranslation",
    #"weblate.machinery.glosbe.GlosbeTranslation",
    #"weblate.machinery.google.GoogleTranslation",
    #"weblate.machinery.googlev3.GoogleV3Translation",
    #"weblate.machinery.microsoft.MicrosoftCognitiveTranslation",
    #"weblate.machinery.microsoftterminology.MicrosoftTerminologyService",
    #"weblate.machinery.modernmt.ModernMTTranslation",
    #"weblate.machinery.mymemory.MyMemoryTranslation",
    #     "weblate.machinery.netease.NeteaseSightTranslation",
    # "weblate.machinery.tmserver.AmagamaTranslation",
    # "weblate.machinery.tmserver.TMServerTranslation",
    #"weblate.machinery.yandex.YandexTranslation",
    "weblate.machinery.weblatetm.WeblateTranslation",
    #     "weblate.machinery.saptranslationhub.SAPTranslationHub",
    #"weblate.machinery.dummy.DummyTranslation",
    #"weblate.machinery.youdao.YoudaoTranslation",
    "weblate.memory.machine.WeblateMemory",
)

# Machine translation API keys

# URL of the Apertium APy server
MT_APERTIUM_APY = None

# DeepL API key
MT_DEEPL_KEY = "1f9bb7b3-3330-80ac-0e0a-810be6c714eb" # DONE

# Microsoft Cognitive Services Translator API, register at
# https://portal.azure.com/
MT_MICROSOFT_COGNITIVE_KEY = "f296e16c97fb43cd9d5ae4ca0b5600d5" # DONE
MT_MICROSOFT_REGION = None

# ModernMT
MT_MODERNMT_KEY = "B984A93B-BC62-4A24-5380-A92680756864"

# MyMemory identification email, see
# https://mymemory.translated.net/doc/spec.php
MT_MYMEMORY_EMAIL = None

# Optional MyMemory credentials to access private translation memory
MT_MYMEMORY_USER = None
MT_MYMEMORY_KEY = None

# Google API key for Google Translate API v2
MT_GOOGLE_KEY = "AIzaSyD7LaCZUkPwRZ67GJH56QjsQgzFYYfiM28" # DONE

# Google Translate API3 credentials and project id
MT_GOOGLE_CREDENTIALS = os.path.join(DATA_DIR, 'config', 'Weblate-9a6e64f2fc95.json')
MT_GOOGLE_PROJECT = '851612429544'

# Baidu app key and secret
MT_BAIDU_ID = "20151113000005349"
MT_BAIDU_SECRET = "osubCEzlGjzvw8qdQc41"

# Youdao Zhiyun app key and secret
MT_YOUDAO_ID = "50f399d98635dd3f"
MT_YOUDAO_SECRET = "S3soUpU3PBiz246SHW2moBi2YSl1w5pn"

# Netease Sight (Jianwai) app key and secret
MT_NETEASE_KEY = None
MT_NETEASE_SECRET = None

# API key for Yandex Translate API
MT_YANDEX_KEY = "trnsl.1.1.20200416T123410Z.9609ceab3378b3a0.ee22e7bd480a84f8e1a27be138983517ccc622de" # DONE

# tmserver URL
MT_TMSERVER = None

# SAP Translation Hub
MT_SAP_BASE_URL = None
MT_SAP_SANDBOX_APIKEY = None
MT_SAP_USERNAME = None
MT_SAP_PASSWORD = None
MT_SAP_USE_MT = True

# Use HTTPS when creating redirect URLs for social authentication, see
# documentation for more details:
# https://python-social-auth-docs.readthedocs.io/en/latest/configuration/settings.html#processing-redirects-and-urlopen
SOCIAL_AUTH_REDIRECT_IS_HTTPS = ENABLE_HTTPS

# Make CSRF cookie HttpOnly, see documentation for more details:
# https://docs.djangoproject.com/en/1.11/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = ENABLE_HTTPS
# Store CSRF token in session
CSRF_USE_SESSIONS = True
# Customize CSRF failure view
CSRF_FAILURE_VIEW = "weblate.trans.views.error.csrf_failure"
SESSION_COOKIE_SECURE = ENABLE_HTTPS
SESSION_COOKIE_HTTPONLY = True
# SSL redirect
SECURE_SSL_REDIRECT = ENABLE_HTTPS
# Sent referrrer only for same origin links
SECURE_REFERRER_POLICY = "same-origin"
# SSL redirect URL exemption list
SECURE_REDIRECT_EXEMPT = (r"healthz/$",)  # Allowing HTTP access to health check
# Session cookie age (in seconds)
SESSION_COOKIE_AGE = 1000
SESSION_COOKIE_AGE_AUTHENTICATED = 1209600
SESSION_COOKIE_SAMESITE = "Lax"
# Increase allowed upload size
DATA_UPLOAD_MAX_MEMORY_SIZE = 50000000
# Allow more fields for case with a lot of subscriptions in profile
DATA_UPLOAD_MAX_NUMBER_FIELDS = 2000

# Apply session coookie settings to language cookie as ewll
LANGUAGE_COOKIE_SECURE = SESSION_COOKIE_SECURE
LANGUAGE_COOKIE_HTTPONLY = SESSION_COOKIE_HTTPONLY
LANGUAGE_COOKIE_AGE = SESSION_COOKIE_AGE_AUTHENTICATED * 10
LANGUAGE_COOKIE_SAMESITE = SESSION_COOKIE_SAMESITE

# Some security headers
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True

# Optionally enable HSTS
SECURE_HSTS_SECONDS = 31536000 if ENABLE_HTTPS else 0
SECURE_HSTS_PRELOAD = ENABLE_HTTPS
SECURE_HSTS_INCLUDE_SUBDOMAINS = ENABLE_HTTPS

# HTTPS detection behind reverse proxy
SECURE_PROXY_SSL_HEADER = None

# URL of login
LOGIN_URL = f"{URL_PREFIX}/accounts/login/"

# URL of logout
LOGOUT_URL = f"{URL_PREFIX}/accounts/logout/"

# Default location for login
LOGIN_REDIRECT_URL = f"{URL_PREFIX}/"

# Anonymous user name
ANONYMOUS_USER_NAME = "anonymous"

# Reverse proxy settings
IP_PROXY_HEADER = "HTTP_X_FORWARDED_FOR"
IP_BEHIND_REVERSE_PROXY = False
IP_PROXY_OFFSET = 0

# Sending HTML in mails
EMAIL_SEND_HTML = True

# Subject of emails includes site title
EMAIL_SUBJECT_PREFIX = f"[{SITE_TITLE}] "

# Enable remote hooks
ENABLE_HOOKS = True

# By default the length of a given translation is limited to the length of
# the source string * 10 characters. Set this option to False to allow longer
# translations (up to 10.000 characters)
LIMIT_TRANSLATION_LENGTH_BY_SOURCE_LENGTH = True

# Use simple language codes for default language/country combinations
SIMPLIFY_LANGUAGES = True

# Render forms using bootstrap
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap3"
CRISPY_TEMPLATE_PACK = "bootstrap3"

# List of quality checks
# CHECK_LIST = (
#     "weblate.checks.same.SameCheck",
#     "weblate.checks.chars.BeginNewlineCheck",
#     "weblate.checks.chars.EndNewlineCheck",
#     "weblate.checks.chars.BeginSpaceCheck",
#     "weblate.checks.chars.EndSpaceCheck",
#     "weblate.checks.chars.DoubleSpaceCheck",
#     "weblate.checks.chars.EndStopCheck",
#     "weblate.checks.chars.EndColonCheck",
#     "weblate.checks.chars.EndQuestionCheck",
#     "weblate.checks.chars.EndExclamationCheck",
#     "weblate.checks.chars.EndEllipsisCheck",
#     "weblate.checks.chars.EndSemicolonCheck",
#     "weblate.checks.chars.MaxLengthCheck",
#     "weblate.checks.chars.KashidaCheck",
#     "weblate.checks.chars.PunctuationSpacingCheck",
#     "weblate.checks.format.PythonFormatCheck",
#     "weblate.checks.format.PythonBraceFormatCheck",
#     "weblate.checks.format.PHPFormatCheck",
#     "weblate.checks.format.CFormatCheck",
#     "weblate.checks.format.PerlFormatCheck",
#     "weblate.checks.format.JavaScriptFormatCheck",
#     "weblate.checks.format.LuaFormatCheck",
#     "weblate.checks.format.ObjectPascalFormatCheck",
#     "weblate.checks.format.SchemeFormatCheck",
#     "weblate.checks.format.CSharpFormatCheck",
#     "weblate.checks.format.JavaFormatCheck",
#     "weblate.checks.format.JavaMessageFormatCheck",
#     "weblate.checks.format.PercentPlaceholdersCheck",
#     "weblate.checks.format.VueFormattingCheck",
#     "weblate.checks.format.I18NextInterpolationCheck",
#     "weblate.checks.format.ESTemplateLiteralsCheck",
#     "weblate.checks.angularjs.AngularJSInterpolationCheck",
#     "weblate.checks.icu.ICUMessageFormatCheck",
#     "weblate.checks.icu.ICUSourceCheck",
#     "weblate.checks.qt.QtFormatCheck",
#     "weblate.checks.qt.QtPluralCheck",
#     "weblate.checks.ruby.RubyFormatCheck",
#     "weblate.checks.consistency.PluralsCheck",
#     "weblate.checks.consistency.SamePluralsCheck",
#     "weblate.checks.consistency.ConsistencyCheck",
#     "weblate.checks.consistency.TranslatedCheck",
#     "weblate.checks.chars.EscapedNewlineCountingCheck",
#     "weblate.checks.chars.NewLineCountCheck",
#     "weblate.checks.markup.BBCodeCheck",
#     "weblate.checks.chars.ZeroWidthSpaceCheck",
#     "weblate.checks.render.MaxSizeCheck",
#     "weblate.checks.markup.XMLValidityCheck",
#     "weblate.checks.markup.XMLTagsCheck",
#     "weblate.checks.markup.MarkdownRefLinkCheck",
#     "weblate.checks.markup.MarkdownLinkCheck",
#     "weblate.checks.markup.MarkdownSyntaxCheck",
#     "weblate.checks.markup.URLCheck",
#     "weblate.checks.markup.SafeHTMLCheck",
#     "weblate.checks.placeholders.PlaceholderCheck",
#     "weblate.checks.placeholders.RegexCheck",
#     "weblate.checks.duplicate.DuplicateCheck",
#     "weblate.checks.source.OptionalPluralCheck",
#     "weblate.checks.source.EllipsisCheck",
#     "weblate.checks.source.MultipleFailingCheck",
#     "weblate.checks.source.LongUntranslatedCheck",
#     "weblate.checks.format.MultipleUnnamedFormatsCheck",
#     "weblate.checks.glossary.GlossaryCheck",
# )

# List of automatic fixups
# AUTOFIX_LIST = (
#     "weblate.trans.autofixes.whitespace.SameBookendingWhitespace",
#     "weblate.trans.autofixes.chars.ReplaceTrailingDotsWithEllipsis",
#     "weblate.trans.autofixes.chars.RemoveZeroSpace",
#     "weblate.trans.autofixes.chars.RemoveControlChars",
# )

# List of enabled addons
# WEBLATE_ADDONS = (
#     "weblate.addons.gettext.GenerateMoAddon",
#     "weblate.addons.gettext.UpdateLinguasAddon",
#     "weblate.addons.gettext.UpdateConfigureAddon",
#     "weblate.addons.gettext.MsgmergeAddon",
#     "weblate.addons.gettext.GettextCustomizeAddon",
#     "weblate.addons.gettext.GettextAuthorComments",
#     "weblate.addons.cleanup.CleanupAddon",
#     "weblate.addons.cleanup.RemoveBlankAddon",
#     "weblate.addons.consistency.LangaugeConsistencyAddon",
#     "weblate.addons.discovery.DiscoveryAddon",
#     "weblate.addons.autotranslate.AutoTranslateAddon",
#     "weblate.addons.flags.SourceEditAddon",
#     "weblate.addons.flags.TargetEditAddon",
#     "weblate.addons.flags.SameEditAddon",
#     "weblate.addons.flags.BulkEditAddon",
#     "weblate.addons.generate.GenerateFileAddon",
#     "weblate.addons.generate.PseudolocaleAddon",
#     "weblate.addons.generate.PrefillAddon",
#     "weblate.addons.json.JSONCustomizeAddon",
#     "weblate.addons.xml.XMLCustomizeAddon",
#     "weblate.addons.properties.PropertiesSortAddon",
#     "weblate.addons.git.GitSquashAddon",
#     "weblate.addons.removal.RemoveComments",
#     "weblate.addons.removal.RemoveSuggestions",
#     "weblate.addons.resx.ResxUpdateAddon",
#     "weblate.addons.yaml.YAMLCustomizeAddon",
#     "weblate.addons.cdn.CDNJSAddon",
# )

# E-mail address that error messages come from.
SERVER_EMAIL = "root@localhost"

# Default email address to use for various automated correspondence from
# the site managers. Used for registration emails.
DEFAULT_FROM_EMAIL = "noreply@weblate.org"

# List of URLs your site is supposed to serve
ALLOWED_HOSTS = ["127.0.0.1"]

# Configuration for caching
CACHES = {
    "default": {
        "BACKEND": "redis_lock.django_cache.RedisCache",
        #'LOCATION': 'redis://127.0.0.1:6379/0',
        "LOCATION": "rediss://127.0.0.1:6378/0",
        "OPTIONS": {"CONNECTION_POOL_KWARGS": {"ssl_cert_reqs": None}},
        # 'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        # 'LOCATION': '127.0.0.1:11211',
    },
    "avatar": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": os.path.join(DATA_DIR, "avatar-cache"),
        "TIMEOUT": 86400,
        "OPTIONS": {"MAX_ENTRIES": 1000},
    },
}

# Store sessions in cache
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# Store messages in session
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

# REST framework settings for API
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    "DEFAULT_PERMISSION_CLASSES": [
        # Require authentication for login required sites
        "rest_framework.permissions.IsAuthenticated"
        if REQUIRE_LOGIN
        else "rest_framework.permissions.IsAuthenticatedOrReadOnly"
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "weblate.api.authentication.BearerAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_THROTTLE_CLASSES": (
        "weblate.api.throttling.UserRateThrottle",
        "weblate.api.throttling.AnonRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {"anon": "100/day", "user": "5000/hour"},
    "DEFAULT_PAGINATION_CLASS": "weblate.api.pagination.StandardPagination",
    "PAGE_SIZE": 50,
    "VIEW_DESCRIPTION_FUNCTION": "weblate.api.views.get_view_description",
    "UNAUTHENTICATED_USER": "weblate.auth.models.get_anonymous",
}

# Fonts CDN URL
FONTS_CDN_URL = "https://s.weblate.org/cdn/"

# Django compressor offline mode
COMPRESS_ENABLED = False
COMPRESS_OFFLINE = False
COMPRESS_OFFLINE_CONTEXT = "weblate.utils.compress.offline_context"

# Require login for all URLs
if REQUIRE_LOGIN:
    LOGIN_REQUIRED_URLS = (r"/(.*)$",)

# In such case you will want to include some of the exceptions
# LOGIN_REQUIRED_URLS_EXCEPTIONS = (
#    rf"{URL_PREFIX}/accounts/(.*)$",  # Required for login
#    rf"{URL_PREFIX}/admin/login/(.*)$",  # Required for admin login
#    rf"{URL_PREFIX}/static/(.*)$",  # Required for development mode
#    rf"{URL_PREFIX}/widgets/(.*)$",  # Allowing public access to widgets
#    rf"{URL_PREFIX}/data/(.*)$",  # Allowing public access to data exports
#    rf"{URL_PREFIX}/hooks/(.*)$",  # Allowing public access to notification hooks
#    rf"{URL_PREFIX}/healthz/$",  # Allowing public access to health check
#    rf"{URL_PREFIX}/api/(.*)$",  # Allowing access to API
#    rf"{URL_PREFIX}/js/i18n/$",  # JavaScript localization
#    rf"{URL_PREFIX}/contact/$",  # Optional for contact form
#    rf"{URL_PREFIX}/legal/(.*)$",  # Optional for legal app
#    rf"{URL_PREFIX}/avatar/(.*)$",  # Optional for avatars
# )

# Silence some of the Django system checks
SILENCED_SYSTEM_CHECKS = [
    # We have modified django.contrib.auth.middleware.AuthenticationMiddleware
    # as weblate.accounts.middleware.AuthenticationMiddleware
    "admin.E408"
]

#REGISTRATION_ALLOW_BACKENDS = ["github", "opensuse", "email", "username"]

INVOICE_PATH = "/home/nijel/weblate/tmp-fakturace/pdf/"
INTERNAL_IPS = ("127.0.0.1",)
SIMPLIFY_LANGUAGES = True

DEMO_SERVER = True

AKISMET_API_KEY = "eef7fc7d6793" # DONE
SPECIAL_CHARS = ("\t", "\r", "\n", "→", "↵", "…", "\u00A0")

STATUS_URL = "https://status.weblate.org/"

# EMAIL_HOST ='xx'

WEBLATE_GPG_IDENTITY = "Weblate <hosted@weblate.org>"

CELERY_TASK_ALWAYS_EAGER = False
CELERY_BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

AUTH_RESTRICT_ADMINS = {
    "xnijel": {
            "trans.add_project",
            "trans.change_project",
            "trans.add_component",
            "trans.change_component",
    }
}


PAYMENT_REDIRECT_URL = "http://localhost:1234/{language}/payment/{uuid}/"
SUPPORT_API_URL = "http://localhost:1234/api/support/"
# RATELIMIT_TRANSLATE_ATTEMPTS = 0


# Celery settings, it is not recommended to change these
CELERY_WORKER_MAX_MEMORY_PER_CHILD = 200000
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_TASK_ROUTES = {
    "weblate.trans.tasks.auto_translate*": {"queue": "translate"},
    "weblate.accounts.tasks.notify_*": {"queue": "notify"},
    "weblate.accounts.tasks.send_mails": {"queue": "notify"},
    "weblate.utils.tasks.settings_backup": {"queue": "backup"},
    "weblate.utils.tasks.database_backup": {"queue": "backup"},
    "weblate.wladmin.tasks.backup": {"queue": "backup"},
    "weblate.wladmin.tasks.backup_service": {"queue": "backup"},
    "weblate.memory.tasks.*": {"queue": "memory"},
}

# Third party services integration
PIWIK_SITE_ID = None
PIWIK_URL = None
SENTRY_DSN = "https://9fb43c408e20485aada26dd71e72e847@sentry.io/1268937"
SENTRY_DSN = "https://959398dd08f24c65bfe60cfb9d82ad01@sentry.weblate.org/2"
SENTRY_TOKEN = "98a12a0298424810bf08d845632d6359c148d847854f45feadd330cc63c58927" # DONE

PAYMENT_FAKTURACE = "/home/nijel/weblate/tmp-fakturace/"


# SAML
import saml2
from saml2.saml import (
    NAMEID_FORMAT_EMAILADDRESS,
    NAMEID_FORMAT_PERSISTENT,
    NAMEID_FORMAT_UNSPECIFIED,
)
from saml2.sigver import get_xmlsec_binary

IDP_URL = 'http://127.0.0.1:8000/idp'
SAML_IDP_CONFIG = {
    'debug' : DEBUG,
    'xmlsec_binary': get_xmlsec_binary(['/opt/local/bin', '/usr/bin/xmlsec1']),
    'entityid': f'{IDP_URL}/metadata',
    'description': 'Example IdP setup',

    'service': {
        'idp': {
            'name': 'Django localhost IdP',
            'endpoints': {
                'single_sign_on_service': [
                    (f'{IDP_URL}/sso/post/', saml2.BINDING_HTTP_POST),
                    (f'{IDP_URL}/sso/redirect/', saml2.BINDING_HTTP_REDIRECT),
                ],
                "single_logout_service": [
                    (f"{IDP_URL}/slo/post/", saml2.BINDING_HTTP_POST),
                    (f"{IDP_URL}/slo/redirect/", saml2.BINDING_HTTP_REDIRECT)
                ],
            },
            'name_id_format': [NAMEID_FORMAT_EMAILADDRESS, NAMEID_FORMAT_UNSPECIFIED, NAMEID_FORMAT_PERSISTENT],
            'sign_response': True,
            'sign_assertion': True,
            'want_authn_requests_signed': False,
        },
    },

    #  openssl req -new -x509 -days 3650 -nodes -out saml.crt -keyout saml.pem
    # Signing
    'key_file': os.path.join(DATA_DIR, "saml", "saml.pem"),
    'cert_file': os.path.join(DATA_DIR, "saml", "saml.crt"),
    # Encryption
    'encryption_keypairs': [{
        'key_file': os.path.join(DATA_DIR, "saml", "saml.pem"),
        'cert_file': os.path.join(DATA_DIR, "saml", "saml.crt"),
    }],
    'valid_for': 365 * 24,
}

# SAML
SOCIAL_AUTH_SAML_SP_PUBLIC_CERT = """
-----BEGIN CERTIFICATE-----
MIIDazCCAlOgAwIBAgIUfwqXmka9MDyNpMNc0BZbu9z+BRUwDQYJKoZIhvcNAQEL
BQAwRTELMAkGA1UEBhMCQ1oxEzARBgNVBAgMClNvbWUtU3RhdGUxITAfBgNVBAoM
GEludGVybmV0IFdpZGdpdHMgUHR5IEx0ZDAeFw0yMDA2MTgxMjE1NTRaFw0zMDA2
MTgxMjE1NTRaMEUxCzAJBgNVBAYTAkNaMRMwEQYDVQQIDApTb21lLVN0YXRlMSEw
HwYDVQQKDBhJbnRlcm5ldCBXaWRnaXRzIFB0eSBMdGQwggEiMA0GCSqGSIb3DQEB
AQUAA4IBDwAwggEKAoIBAQC5cUcnOJ/4Wqno4mb1X4Ft1ou2KQ8D+NA2OurLr895
os3mFpZpY6IVnnsMFqVMoCKfOOVb5RVzWyC0rza6yv2lNThoqdKee3/tYEp2rBlF
H3tuDXi5tFasPqVq+lpav/+k8x7ILYCWk5hJJPGEpEWmzjrJKCTFH5EEuavsEqC7
RcrIlxLlSfZ6vW3+5RXqgq1IpcIs2X0Gbc69ieFBLuDF+ms+rGjafLsTd1dSP2ld
umI7mwm+TeGvjyK3nLHAqPyAClrcIrXhROdBYdrN0T6UJlTO9NU9bNzTSICLrt9m
tXhNBJuLMQDFqgJ+kwJaAHt8HG7oTZtqs7fO8X7/O+PHAgMBAAGjUzBRMB0GA1Ud
DgQWBBQuDG1nXoTTOCoXfp0/W1iyHKPQsjAfBgNVHSMEGDAWgBQuDG1nXoTTOCoX
fp0/W1iyHKPQsjAPBgNVHRMBAf8EBTADAQH/MA0GCSqGSIb3DQEBCwUAA4IBAQCp
p3Epi5MSQwClEssV966POaL60v8YCjyFdXKxeBjdST22/0zHsSIrbloPYzag2RCV
agQml8JT+s9M2pgRkSZzCQX/KYcBSkeqg/4eCPpnkLZy/sriKMcwXr21x7j0V75K
zNTHI/RkJEShiBqQrYiu6KEXkhyIfdpE+N2OIVuZG/xPkj5cC4q/o/6mdd75qDNd
kCIukO93TZIyryjnLBFxKMi3d/uvvSCiYyGYxiEyhfrw3KKgdbiz6d82DL4htFkh
Qb69WNrIlvxKxnVCzE891Ryjzk0BVG6N6XL5Bt+y/hqsc9GsvMNBPAkrzrC0LDr5
jwMptFAxRPHgZyj1NnC/
-----END CERTIFICATE-----
"""
SOCIAL_AUTH_SAML_SP_PRIVATE_KEY = """
-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC5cUcnOJ/4Wqno
4mb1X4Ft1ou2KQ8D+NA2OurLr895os3mFpZpY6IVnnsMFqVMoCKfOOVb5RVzWyC0
rza6yv2lNThoqdKee3/tYEp2rBlFH3tuDXi5tFasPqVq+lpav/+k8x7ILYCWk5hJ
JPGEpEWmzjrJKCTFH5EEuavsEqC7RcrIlxLlSfZ6vW3+5RXqgq1IpcIs2X0Gbc69
ieFBLuDF+ms+rGjafLsTd1dSP2ldumI7mwm+TeGvjyK3nLHAqPyAClrcIrXhROdB
YdrN0T6UJlTO9NU9bNzTSICLrt9mtXhNBJuLMQDFqgJ+kwJaAHt8HG7oTZtqs7fO
8X7/O+PHAgMBAAECggEAQcsjB5Nbjm38YpgRF3WvIh1ArHycyzf4B4WX0HSsE+fj
TYMuEm47D5iO55cRRsJ6BivVlGkO10K5s+GGdXeXzom3XcsC4x/GH55OTRR6Ur/8
tusorhqBtdL0NaRlclU0in2HqlYajVIIccsdtYXjAG+jA8OuaBHvDdIiYTuqs0ZQ
+63rCwmEUVNtuX+hx7O38pASQciYOvhm9RVlpadQlye6wNK19k2DYpwUtTKeJFJL
70HKL14RcKQgB1qpv+an3DuMX4TmxAJs0N1KJCYvvRz/o74BMxEOLnNvvzsV+UB4
9GI2aSidbDRwE5VwwF7QfCVEIu+Eazt6wbOvSG6s4QKBgQDl2Bav0QeKekk2ts69
jAtkhjoUCTEH1g6K8k8WtOnmyqlDccsaguU/HqKlRVsRAz7Rq80gnP8Yd0cE5pde
uw2SyqNE+SQgbI9ncJb1xYTc7u/aGs9JRZ1+HOfbOXwnem3/K4I1u3keQp8iFSo6
4L/d38sGI0e6EAbRH6poxTnJLQKBgQDOi6nuGbbTHD7Z0fWLPdxFH4TzINon56gK
WbFQkdoRjz3B1+r2x/EKmRpfgbxG1md64JjqZP5F/0cYoCbTdMHzKtFYcLLa8JQF
N919evkPedN4iaF2dw7+LxI7VVZ3DKpF3BzbRVuYHuB2t6Z5ddJ20tG8h64eAo3U
4Tw+CWlRQwKBgCI6rCZC2vykeYLMdr2Dva6azsttEwA3wLKwo1aeWrckN1D0AWtR
UxKzXUV/rrA564EONN5GgzcBjHIOZTyWXs8dnnMHJ3ossK6W9eRkJgVBEDdLBtPC
qlG9vEnJpdO7R+ZYdGvMH52CDnDk9gUOs4Q3b+TaHDR5bop2TMqNlK2BAoGBAI1F
5hMfr3cySKMAAy0cQL9e0bbib5T/1GZP9wIe4MNF8H3Xy7TECVCwa+OLf1YMbHcV
jEI2ld0WwHBNioDzyX0jelE9tHggOX5gObUMGbLGJyi5KqE2yiB93cCLnDqNhSGH
bo1kIUQpSmqpLsrBFhWEGUUUoLmSEaTb8jKUiV61AoGBAOLWJw2DODecH3tEPZbm
jw+n/dlPvoDM6nyTK2X/gS3PtDMj0AcNqlNG7ROcEii/tSX14XagXgUDG9mvqO7E
4RNAM+cItoEUD5pHSHKEhQDH45+OcDxABr0NL61NpwVkedpijbj0586FtsVYnCR4
0y4m+2VscZAZrG0EN4rhVPOE
-----END PRIVATE KEY-----
"""
SOCIAL_AUTH_SAML_ENABLED_IDPS = {
    "weblate": {
        "entity_id": "https://hosted.weblate.org/idp/metadata/",
        "url": "https://idp.testshib.org/idp/profile/SAML2/Redirect/SSO",
        "x509cert": "MIIEDjCCAvagAwIBAgIBADA ... 8Bbnl+ev0peYzxFyF5sQA==",
        "attr_name": "full_name",
        "attr_username": "username",
        "attr_email": "email",
    }
}
SOCIAL_AUTH_SAML_SUPPORT_CONTACT = SOCIAL_AUTH_SAML_TECHNICAL_CONTACT = {
    "givenName": ADMINS[0][0],
    "emailAddress": ADMINS[0][1],
}
SITE_URL = "{}://{}".format("https" if ENABLE_HTTPS else "http", SITE_DOMAIN)
SOCIAL_AUTH_SAML_ORG_INFO = {
    "en-US": {
        "name": "weblate",
        "displayname": SITE_TITLE,
        "url": SITE_URL,
    }
}

LOCALIZE_CDN_URL = "file:////tmp/weblateCDN/"
LOCALIZE_CDN_PATH = "/tmp/weblateCDN/"
HIDE_VERSION = True
SUPPORT_URL = "https://care.weblate.org/"

DEBUG_TOOLBAR_CONFIG = {
    "PROFILER_MAX_DEPTH": 20,
}
EXTRA_HTML_HEAD = '<link href="https://fosstodon.org/@weblate" rel="me">'
