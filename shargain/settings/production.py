from .base import *

DEBUG = False

ALLOWED_HOSTS = ["*"]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console_info": {
            "level": "ERROR",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        }
    },
    "formatters": {
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}] {message}",
            "style": "{",
        }
    },
    "loggers": {
        "django": {
            "handlers": ["console_info"],
        }
    },
}
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "postgres"),
        "USER": os.environ.get("POSTGRES_USER", "postgres"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
    }
}

# On server static and media files are stored outside BASE_DIR
STATIC_ROOT = BASE_DIR.joinpath("static")
MEDIA_ROOT = BASE_DIR.joinpath("media")
