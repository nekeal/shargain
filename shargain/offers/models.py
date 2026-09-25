from typing import Any, TypedDict
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.postgres.indexes import HashIndex
from django.db import models
from django.db.models import Manager, Q, QuerySet
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_better_admin_arrayfield.models.fields import ArrayField

from shargain.accounts.models import CustomUser
from shargain.commons.models import TimeStampedModel
from shargain.offers.db_fields import PydanticField
from shargain.offers.field_extraction import NotificationFieldsSelection


class ScrappingTarget(models.Model):  # type: ignore[django-manager-missing]
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

    filters = models.JSONField(
        verbose_name=_("Notification filters"),
        help_text=_("Filter rules to apply before sending notifications"),
        blank=True,
        null=True,
        default=None,
    )
    show_location_map_in_notifications = models.BooleanField(
        _("Show location map in notifications"),
        help_text=_("If True, a Google Maps link will be appended to Telegram notifications for offers from this URL."),
        default=False,
    )
    waypoints = models.JSONField(
        verbose_name=_("Waypoints"),
        help_text=_('List of waypoints. Format: [{"name": ..., "lat": ..., "lon": ...}]'),
        blank=True,
        null=True,
        default=None,
    )

    notification_fields = PydanticField(
        NotificationFieldsSelection,
        verbose_name=_("Notification fields"),
        help_text=_("Field names from plugins to include in notification messages"),
        null=True,
        blank=True,
        default=None,
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


def get_default_metadata():
    return {"extra": {}}


class OfferMetadata(TypedDict, total=False):
    extra: dict[str, Any]


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

    metadata = models.JSONField(
        verbose_name=_("Metadata"),
        default=get_default_metadata,
        blank=True,
        help_text=_(
            "Metadata for the offer. Use 'extra' key for unstructured scraper data. "
            "Root level is reserved for official contract fields."
        ),
    )

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
        indexes = [
            HashIndex(fields=["url"], name="offer_url_hash_idx"),
        ]

    def __str__(self) -> str:
        return self.title

    @property
    def domain(self):
        return urlparse(self.url).netloc


class OfferLike(TimeStampedModel):
    """A user marked an offer as liked, from any channel."""

    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name=_("Offer"),
    )

    # Authenticated surface (e.g. web dashboard). Either this or liker_label is set.
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="offer_likes",
        null=True,
        blank=True,
        verbose_name=_("Owner"),
    )

    # Anonymous surface (e.g. Telegram). Free-form identity string.
    liker_label = models.CharField(_("Liker label"), max_length=255, blank=True)

    class Meta:
        verbose_name = _("Offer like")
        verbose_name_plural = _("Offer likes")
        ordering = ["offer_id", "pk"]
        constraints = [
            # Exactly one identity source: a known account or an identity label.
            models.CheckConstraint(
                condition=Q(owner__isnull=False) | ~Q(liker_label=""),
                name="offer_like_has_identity",
            ),
            # Idempotent likes: a known user can like an offer only once.
            models.UniqueConstraint(
                fields=["offer", "owner"],
                name="uniq_offer_like_owner",
                condition=Q(owner__isnull=False),
            ),
            # Idempotent likes: an anonymous liker can like an offer only once.
            models.UniqueConstraint(
                fields=["offer", "liker_label"],
                name="uniq_offer_like_label",
                condition=~Q(liker_label=""),
            ),
        ]

    def __str__(self) -> str:
        identity = self.liker_label or f"user#{self.owner_id}"
        offer_name = self.offer.title if self.offer_id else "Unknown offer"
        return f"{identity} liked {offer_name}"
