import uuid
import warnings

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class NotificationChannelChoices(models.TextChoices):
    DISCORD = "discord", "Discord"
    TELEGRAM = "telegram", "Telegram"


def get_random_register_token():
    return uuid.uuid1().hex


class NotificationConfig(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=100)
    channel = models.CharField(
        verbose_name=_("Channel"),
        max_length=200,
        choices=NotificationChannelChoices.choices,
    )
    webhook_url = models.URLField(verbose_name=_("Webhook url"), blank=True)
    _token = models.CharField(verbose_name=_("Token"), max_length=100, blank=True)
    register_token = models.CharField(
        verbose_name=_("Register token"),
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        default=get_random_register_token,
        help_text=_("Token used to register the channel (chat_id)"),
    )
    chatid = models.CharField(verbose_name=_("Chat ID"), max_length=100, blank=True)

    class Meta:
        verbose_name = _("Notification channel")
        verbose_name_plural = _("Notification channels")

    def __str__(self):
        return self.name

    @property
    def token(self):
        """
        token parameter is deprecated and should no longer be used.
        This property provides backward compatibility.
        :return: Token from settings
        """
        warnings.warn(
            "Token parameter is deprecated and should no longer be used.",
            DeprecationWarning,
        )
        return settings.TELEGRAM_BOT_TOKEN
