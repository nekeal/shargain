from datetime import timedelta
from typing import List, Optional, Tuple, Union

from django.contrib import admin
from django.db.models.expressions import F
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy
from django.utils.translation import ugettext as _
from django_admin_display import admin_display
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin
from django_better_admin_arrayfield.models.fields import ArrayField

from shargain.offers.models import Offer, ScrapingUrl, ScrappingTarget
from shargain.offers.widgets import AdminDynamicArrayWidget


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    exclude = ("main_image_url",)
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
        ("closed_at", admin.filters.EmptyFieldListFilter),  # type: ignore
    ]
    ordering = ("-published_at",)
    search_fields = ("title",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(duration=F("closed_at") - F("created_at"))

    @admin_display(short_description=gettext_lazy("Title"), admin_order_field="title")
    def get_title(self, obj):
        return render_to_string(
            "admin/fields/main_image_offer.html", context={"obj": obj}
        )

    @admin_display(short_description=gettext_lazy("Link to offer"))
    def get_link(self, obj):
        button_text = _("Go to offer")
        return mark_safe(f'<a href="{obj.url}" target="_blank">{button_text}</a>')

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
        admin_order_field="duration",
    )
    def get_duration(self, obj):
        if obj.closed_at:
            seconds = round((obj.closed_at - obj.created_at).total_seconds())
            return timedelta(seconds=seconds)


class ScrapingUrlInlineAdmin(admin.TabularInline):
    model = ScrapingUrl
    show_change_link = True


@admin.register(ScrappingTarget)
class ScrappingTargetAdmin(admin.ModelAdmin, DynamicArrayMixin):
    fields = (
        "name",
        "url",
        "enable_notifications",
        "is_active",
        "notification_config",
        "display_grafana_panel",
    )
    list_display = ("name", "enable_notifications", "is_active")
    readonly_fields = ("display_grafana_panel",)
    formfield_overrides = {ArrayField: {"widget": AdminDynamicArrayWidget}}
    inlines = [ScrapingUrlInlineAdmin]

    def get_readonly_fields(
        self, request: HttpRequest, obj: Optional[ScrappingTarget] = None
    ) -> Union[List[str], Tuple]:
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj:
            readonly_fields.append("name")
        return readonly_fields

    @admin_display(
        short_description=gettext_lazy("Stats"),
    )
    def display_grafana_panel(self, obj):
        return render_to_string("admin/grafana_panels.html", context={"obj": obj})


@admin.register(ScrapingUrl)
class ScrapingUrlAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "scraping_target", "get_scraping_urls")
    search_fields = ("url",)

    @staticmethod
    def get_scraping_urls(obj: ScrapingUrl) -> str:
        return mark_safe(
            f"<a href={obj.url} target=_blank>"
            f"<div style='width:100%'>"
            f"<i class='fas fa-external-link-alt'></i>"
            f"</div>"
            f"</a>"
        )
