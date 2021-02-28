from django.db import models
from django.utils.translation import gettext_lazy as _

from shargain.commons.models import TimeStampedModel


class ScrappingTarget(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=100)
    url = models.URLField()

    notification_config = models.ForeignKey(
        verbose_name=_("Notification channel"),
        to="notifications.NotificationConfig",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Scrapping target")
        verbose_name_plural = _("Scrapping targets")


class Offer(TimeStampedModel):
    url = models.URLField()
    title = models.CharField(verbose_name=_("Title"), max_length=200)
    price = models.IntegerField(verbose_name=_("Price"), blank=True, null=True)

    target = models.ForeignKey(
        verbose_name=_("Target"), to="ScrappingTarget", on_delete=models.PROTECT
    )

    published_at = models.DateTimeField(
        verbose_name=_("Published at"), blank=True, null=True
    )
    closed_at = models.DateTimeField(verbose_name=_("Closed at"), blank=True, null=True)

    class Meta:
        verbose_name = _("Offer")
        verbose_name_plural = _("Offers")
