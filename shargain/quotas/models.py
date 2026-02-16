from django.db import models
from django.utils.translation import gettext_lazy as _

from shargain.accounts.models import CustomUser
from shargain.commons.models import TimeStampedModel
from shargain.quotas.querysets import OfferQuotaQuerySet


class OfferQuota(TimeStampedModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="offer_quotas")
    target = models.ForeignKey("offers.ScrappingTarget", on_delete=models.CASCADE, related_name="quotas")
    max_offers_per_period = models.PositiveIntegerField()
    used_offers_count = models.PositiveIntegerField(default=0)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    auto_renew = models.BooleanField(default=True)
    is_free_tier = models.BooleanField(default=True)

    objects = OfferQuotaQuerySet.as_manager()

    class Meta:
        verbose_name = _("Offer quota")
        verbose_name_plural = _("Offer quotas")
        constraints = [
            models.UniqueConstraint(
                fields=("user", "target", "period_start"),
                name="quotas_offerquota_user_target_start",
            ),
        ]

    def __str__(self) -> str:
        return f"OfferQuota(user={self.user_id}, target={self.target_id}, period_start={self.period_start})"


class ScrapingUrlQuota(TimeStampedModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="scraping_url_quota")
    max_urls = models.PositiveIntegerField()

    class Meta:
        verbose_name = _("Scraping URL quota")
        verbose_name_plural = _("Scraping URL quotas")

    def __str__(self) -> str:
        return f"ScrapingUrlQuota(user={self.user_id}, max_urls={self.max_urls})"
