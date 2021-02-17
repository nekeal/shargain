from django.db import models

from shargain.commons.models import TimeStampedModel


class ScrappingTarget(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField()

    notification_channel = models.ForeignKey(
        "notifications.NotificationChannel",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name


class Offer(TimeStampedModel):
    url = models.URLField()
    title = models.CharField(max_length=200)
    price = models.IntegerField(blank=True, null=True)

    target = models.ForeignKey(ScrappingTarget, on_delete=models.PROTECT)

    published_at = models.DateTimeField(blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)
