from .base import *

SECRET_KEY = "secret_key"
ALLOWED_HOSTS = ["*"]

# ------------- DATABASES -------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", "shargain"),
        "USER": env("POSTGRES_USER", "shargain"),
        "PASSWORD": env("POSTGRES_PASSWORD", "shargain"),
        "HOST": env("POSTGRES_HOST", "localhost"),
    }
}

# ------------- SECURITY -------------
CSRF_TRUSTED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000", "https://3000-oc.bcode.app", "https://8000-oc.bcode.app"]
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = CSRF_TRUSTED_ORIGINS

# ------------- LOGGING -------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "shargain": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}
