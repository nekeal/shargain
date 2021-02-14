from .base import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "shargain"),
        "USER": os.environ.get("POSTGRES_USER", "shargain"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "shargain"),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
    }
}
