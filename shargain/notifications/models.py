from django.db import models


class NotificationPlatformChoices(models.TextChoices):
    DISCORD = "discord", "Discord"
    TELEGRAM = "telegram", "Telegram"


class NotificationChannel(models.Model):
    name = models.CharField(max_length=100)
    platform = models.CharField(
        max_length=200, choices=NotificationPlatformChoices.choices
    )
    webhook_url = models.URLField(blank=True)
    token = models.CharField(max_length=100, blank=True)
