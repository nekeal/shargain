"""Models for Telegram integration."""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class TelegramUser(models.Model):
    """Links a Telegram account to one or more Shargain users."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="telegram_accounts",
        verbose_name=_("User"),
    )
    telegram_id = models.CharField(
        max_length=64,
        verbose_name=_("Telegram ID"),
        help_text=_("Unique identifier of the Telegram user"),
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name=_("Is active"),
        help_text=_("Whether notifications are enabled for this Telegram account."),
    )

    class Meta:
        unique_together = ("user", "telegram_id")
        verbose_name = _("Telegram user")
        verbose_name_plural = _("Telegram users")
        ordering = ["user_id"]

    def __str__(self) -> str:
        return f"{self.user} -> {self.telegram_id}"


def get_default_register_token():
    return uuid.uuid4().hex


class TelegramRegisterToken(models.Model):
    """Stores registration tokens used to link Telegram accounts."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="telegram_register_tokens",
        verbose_name=_("User"),
    )
    register_token = models.CharField(
        max_length=100,
        unique=True,
        default=get_default_register_token,
        verbose_name=_("Register token"),
    )
    is_used = models.BooleanField(
        default=False,
        verbose_name=_("Is used"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("Telegram register token")
        verbose_name_plural = _("Telegram register tokens")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        status = "used" if self.is_used else "unused"
        return f"{self.register_token} ({status})"
