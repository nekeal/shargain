from urllib.parse import urlparse

from django.db import models
from django.db.models import Manager, QuerySet
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_better_admin_arrayfield.models.fields import ArrayField

from shargain.accounts.models import CustomUser
from shargain.commons.models import TimeStampedModel


class ScrappingTarget(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=100)
    url = ArrayField(models.URLField(max_length=1024), default=list, blank=True)
    enable_notifications = models.BooleanField(_("Enable notifications"), default=True)
    is_active = models.BooleanField(
        _("Is active"),
        help_text=_("Defines whether this target should be scrapped"),
        default=True,
    )

    notification_config = models.ForeignKey(
        verbose_name=_("Notification channel"),
        to="notifications.NotificationConfig",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    owner = models.ForeignKey(
        CustomUser, verbose_name=_("Owner"), null=True, on_delete=models.CASCADE, related_name="scraping_targets"
    )

    class Meta:
        verbose_name = _("Scrapping target")
        verbose_name_plural = _("Scrapping targets")

    def __str__(self):
        return f"{self.name} ({self.id})"


class ScrapingUrl(models.Model):
    name = models.CharField(_("Name"), max_length=255, help_text=_("Human readable name for the URL"))
    url = models.URLField(
        _("Target URL"),
        max_length=1024,
        help_text=_("Target URL to one of the supported sites"),
    )
    is_active = models.BooleanField(
        _("Is active"),
        help_text=_("Defines whether this url should be scrapped"),
        default=True,
    )

    scraping_target = models.ForeignKey(
        ScrappingTarget,
        verbose_name=_("Scraping target"),
        on_delete=models.CASCADE,
        help_text=_("Group of scraping URLs"),
    )

    class Meta:
        verbose_name = _("Scraping URL")
        verbose_name_plural = _("Scraping URLs")

    def __str__(self):
        return f"{self.id}: {self.name}"


class ScrapingCheckin(models.Model):
    scraping_url = models.ForeignKey("offers.ScrapingUrl", on_delete=models.CASCADE, related_name="checkins")
    timestamp = models.DateTimeField(auto_now_add=True)
    offers_count = models.PositiveIntegerField()
    new_offers_count = models.PositiveIntegerField()

    class Meta:
        verbose_name = _("Scraping checkin")
        verbose_name_plural = _("Scraping checkins")

    def __str__(self):
        return f"Checkin for {self.scraping_url} at {self.timestamp}"


class OfferQueryset(QuerySet):
    def opened(self):
        return self.filter(closed_at=None)

    def closed(self):
        return self.exclude(closed_at=None)

    def olx(self):
        return self.filter(url__contains="olx.pl")

    def otomoto(self):
        return self.filter(url__contains="otomoto.pl")

    def with_source_html(self):
        return self.exclude(source_html="")


def get_offer_source_html_path(instance: "Offer", filename: str):
    _date = instance.published_at or timezone.localtime()
    return f"offer_sources/{_date.year}/{_date.month:02}/{_date.day:02}/{slugify(instance.title)}_{instance.id}.html"


class Offer(TimeStampedModel):
    url = models.URLField(max_length=1024)
    title = models.CharField(verbose_name=_("Title"), max_length=200)
    price = models.IntegerField(verbose_name=_("Price"), blank=True, null=True)
    main_image_url = models.URLField(_("Main image's URL"), blank=True, max_length=1024)
    source_html = models.FileField(verbose_name=_("Source HTML"), upload_to=get_offer_source_html_path, blank=True)
    list_url = models.URLField(
        _("List URL"),
        max_length=1024,
        blank=True,
        null=False,
        help_text=_("URL of the page where this offer was found"),
    )

    target = models.ForeignKey(verbose_name=_("Target"), to="ScrappingTarget", on_delete=models.PROTECT)

    published_at = models.DateTimeField(verbose_name=_("Published at"), blank=True, null=True)
    closed_at = models.DateTimeField(verbose_name=_("Closed at"), blank=True, null=True)
    last_check_at = models.DateTimeField(
        verbose_name=_("Last check at"),
        help_text=_("Time of last offer check"),
        default=timezone.localtime,
    )

    objects = Manager.from_queryset(OfferQueryset)()

    class Meta:
        verbose_name = _("Offer")
        verbose_name_plural = _("Offers")

    @property
    def domain(self):
        return urlparse(self.url).netloc


class OfferQuota(TimeStampedModel):
    """
    Model to track offer quota for targets.
    This provides a scalable foundation for a future subscription and billing system.
    """

    target = models.ForeignKey(
        ScrappingTarget,
        verbose_name=_("Target"),
        on_delete=models.CASCADE,
        related_name="offer_quotas",
    )
    max_offers_per_period = models.PositiveIntegerField(
        verbose_name=_("Max offers per period"),
        help_text=_("Maximum number of offers allowed in the period"),
        null=True,
        blank=True,
    )
    used_offers_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Used offers count"),
        help_text=_("Number of offers used in the current period"),
    )
    period_start = models.DateTimeField(
        verbose_name=_("Period start"),
        help_text=_("Start of the current quota period"),
    )
    period_end = models.DateTimeField(
        verbose_name=_("Period end"),
        help_text=_("End of the current quota period"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Offer quota")
        verbose_name_plural = _("Offer quotas")

    def __str__(self):
        return f"Quota for {self.target.name}"

    @property
    def remaining_offers(self):
        """Number of offers that can still be created in the current period."""
        if self.max_offers_per_period is None:  # Unlimited offers
            return float("inf")
        return max(0, self.max_offers_per_period - self.used_offers_count)

    @property
    def is_exhausted(self):
        """Whether the quota limit has been reached."""
        if self.max_offers_per_period is None:  # Unlimited offers
            return False
        return self.used_offers_count >= self.max_offers_per_period
