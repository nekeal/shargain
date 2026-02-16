from django.contrib import admin

from shargain.quotas.models import OfferQuota, ScrapingUrlQuota


@admin.register(OfferQuota)
class OfferQuotaAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "target",
        "used_offers_count",
        "max_offers_per_period",
        "period_start",
        "period_end",
        "auto_renew",
        "is_free_tier",
    )
    list_filter = ("auto_renew", "is_free_tier")
    search_fields = ("user__username", "target__name")


@admin.register(ScrapingUrlQuota)
class ScrapingUrlQuotaAdmin(admin.ModelAdmin):
    list_display = ("user", "max_urls")
    search_fields = ("user__username",)
