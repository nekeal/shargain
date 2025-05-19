import secrets
from datetime import timedelta
from functools import partial

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    pass


def get_default_valid_until():
    return timezone.localtime() + timedelta(days=1)


class RegisterToken(models.Model):
    token = models.CharField(max_length=32, default=partial(secrets.token_hex, 16), unique=True)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(default=get_default_valid_until)
    already_used = models.BooleanField(default=False)

    def __str__(self):
        return self.token

    class Meta:
        verbose_name = _("Register token")
        verbose_name_plural = _("Register tokens")
