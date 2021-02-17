from django.contrib import admin
from django.utils.safestring import mark_safe
from django_admin_display import admin_display

from shargain.offers.models import Offer, ScrappingTarget


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "get_is_open", "get_link", "published_at")
    list_filter = ["target", "url"]
    ordering = ("-published_at",)

    def get_link(self, obj):
        return mark_safe(f"<a href='{obj.url}'>Przejdz do oferty</a>")

    @admin_display(
        short_description="Otwarte", boolean=True, admin_order_field="closed_at"
    )
    def get_is_open(self, obj):
        return not bool(obj.closed_at)


@admin.register(ScrappingTarget)
class ScrappingTargetAdmin(admin.ModelAdmin):
    pass
    # list_display = ("title", )
