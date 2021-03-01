from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy
from django.utils.translation import ugettext as _
from django_admin_display import admin_display

from shargain.offers.models import Offer, ScrappingTarget


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "get_is_open", "get_link", "published_at")
    list_filter = ["target", ]
    ordering = ("-published_at",)

    @admin_display(short_description=gettext_lazy("Link to offer"))
    def get_link(self, obj):
        button_text = _("Go to offer")
        return mark_safe(f"<a href='{obj.url}'>{button_text}</a>")

    @admin_display(
        short_description=gettext_lazy("Opened"),
        boolean=True,
        admin_order_field="closed_at",
    )
    def get_is_open(self, obj):
        return not bool(obj.closed_at)


@admin.register(ScrappingTarget)
class ScrappingTargetAdmin(admin.ModelAdmin):
    pass
