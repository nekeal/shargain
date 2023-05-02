from pathlib import Path

from django.utils.translation import gettext_lazy as _
from environs import Env, load_dotenv

env = Env()
load_dotenv(".env")

PROJECT_NAME = "shargain"

BASE_DIR = Path(__file__).parents[2]

APPS_DIR = BASE_DIR.joinpath(PROJECT_NAME)

DEBUG = True

ALLOWED_HOSTS = []

# ------------- APPS -------------
DJANGO_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "dbbackup",
    "rest_framework",
    "drf_yasg",
    "debug_toolbar",
    "django_extensions",
    "celery",
    "django_filters",
    "corsheaders",
    "django_better_admin_arrayfield",
]

LOCAL_APPS = [
    "shargain.commons.apps.CommonsConfig",
    "shargain.accounts.apps.AccountsConfig",
    "shargain.offers.apps.OffersConfig",
    "shargain.notifications.apps.NotificationsConfig",
    "shargain.scrapper",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ------------- MIDDLEWARES -------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ------------- URLS -------------
ROOT_URLCONF = "shargain.urls"
WSGI_APPLICATION = "shargain.wsgi.application"

# ------------- TEMPLATES -------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR.joinpath("templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ------------- PASSWORDS -------------
AUTH_USER_MODEL = "accounts.CustomUser"

PASSOWRD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.BCryptPasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# ------------- MODELS -------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------- INTERNALIZATION -------------
LANGUAGE_CODE = "en-us"

LOCALE_PATHS = [BASE_DIR.joinpath(PROJECT_NAME).joinpath("locale")]

TIME_ZONE = "Europe/Warsaw"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# ------------- STATIC -------------
STATICFILES_DIRS = []

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR.joinpath("public")

# ------------- MEDIA -------------
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR.joinpath("media")


# ------------- DEBUG TOOLBAR ------------

INTERNAL_IPS = [
    "127.0.0.1",
]

# ------------- REST -------------
CORS_ALLOW_ALL_ORIGINS = True
REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 100,
}

# ------------- JAZZMIN -------------
JAZZMIN_UI_TWEAKS = {
    "navbar": "navbar-dark",
    "theme": "cyborg",
}
JAZZMIN_SETTINGS = {
    "site_brand": "Shargain",
    "site_title": "Shargain",
    "site_header": "Shargain",
    "welcome_sign": _("Snap bargain with Shargain"),
}

# ------------- NOTIFICATIONS -------------
TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_WEBHOOK_URL = env("TELEGRAM_WEBHOOK_URL", "")
