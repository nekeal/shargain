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
    """
    Model for storing Telegram registration tokens.
    Each token is used to link a Telegram account to a user account.
    """

    name = models.CharField(max_length=100, blank=True, help_text="Optional name to recognize tokens")

    register_token = models.CharField(max_length=100, unique=True, default=get_default_register_token)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="telegram_tokens")
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user} - {'Used' if self.is_used else 'Active'}"
