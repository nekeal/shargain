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

# origins
CSRF_TRUSTED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
