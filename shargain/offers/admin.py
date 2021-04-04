import textwrap
from datetime import timedelta

from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy
from django.utils.translation import ugettext as _
from django_admin_display import admin_display

from shargain.offers.models import Offer, ScrappingTarget


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = (
        "get_title",
        "price",
        "get_link",
        "published_at",
        "get_closed_at",
        "get_duration",
    )
    list_filter = [
        "target",
    ]
    ordering = ("-published_at",)

    @admin_display(short_description=gettext_lazy("Title"), admin_order_field="title")
    def get_title(self, obj):
        return mark_safe("<br>".join(textwrap.wrap(obj.title, width=30)))

    @admin_display(short_description=gettext_lazy("Link to offer"))
    def get_link(self, obj):
        button_text = _("Go to offer")
        return mark_safe(f"<a href='{obj.url}'>{button_text}</a>")

    @admin_display(
        short_description=gettext_lazy("Closed at"),
        admin_order_field="closed_at",
    )
    def get_closed_at(self, obj):
        css_class = "btn-outline-danger" if obj.closed_at else "btn-outline-success"
        if obj.closed_at:
            return mark_safe(
                f"<div class='{css_class}'>"
                f"{obj.closed_at.strftime('%d-%m-%y %H:%M')}"
                f"</div>"
            )

    @admin_display(
        short_description=gettext_lazy("Duration"),
    )
    def get_duration(self, obj):
        if obj.closed_at:
            seconds = round((obj.closed_at - obj.created_at).total_seconds())
            return timedelta(seconds=seconds)


@admin.register(ScrappingTarget)
class ScrappingTargetAdmin(admin.ModelAdmin):
    pass
