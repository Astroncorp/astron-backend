from pathlib import Path

from decouple import Csv, config
from django.urls import reverse_lazy

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = config("SECRET_KEY")

DEBUG = config("DEBUG", cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())


INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # extra
    "markdownx",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    # local
    "users",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


AUTH_PASSWORD_VALIDATORS = []


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.User"

# static files
STATIC_URL = "static/"
STATIC_ROOT = "static"

# media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

PAYME_KEY = config("PAYME_KEY")

UNFOLD = {
    "SITE_TITLE": "Admin Panel",
    "SITE_HEADER": "Astron",
    "SITE_SUBHEADER": "Admin Panel",
    "SITE_ICON": {
        "light": lambda request: "https://astron.uz/favicon.ico",
        "dark": lambda request: "https://astron.uz/favicon.ico",
    },
    "SHOW_HISTORY": True,
    "SIDEBAR": {
        "navigation": [
            {
                "title": "Asosiy",
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": "Foydalanuvchilar",
                        "link": reverse_lazy("admin:users_user_changelist"),
                    },
                    {
                        "title": "Reklamalar",
                        "link": reverse_lazy("admin:users_advertisement_changelist"),
                    },
                    {
                        "title": "E'lonlar",
                        "link": reverse_lazy("admin:users_announcement_changelist"),
                    },
                    {
                        "title": "Kanallar",
                        "link": reverse_lazy("admin:users_channel_changelist"),
                    },
                    {
                        "title": "Sanagichlar",
                        "link": reverse_lazy("admin:users_count_changelist"),
                    },
                    {
                        "title": "Fan sanagich",
                        "link": reverse_lazy("admin:users_fansanagich_changelist"),
                    },
                    {
                        "title": "Online kurslar",
                        "link": reverse_lazy("admin:users_coursechannel_changelist"),
                    },
                    {
                        "title": "Postlar",
                        "link": reverse_lazy("admin:users_post_changelist"),
                    },
                    {
                        "title": "Bonuslar",
                        "link": reverse_lazy("admin:users_bonus_changelist"),
                    },
                ],
            }
        ]
    },
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://webapp.astron.uz",
]
CORS_ORIGIN_ALLOW_ALL = True
