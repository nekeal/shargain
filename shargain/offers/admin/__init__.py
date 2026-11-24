from datetime import timedelta

from django.contrib import admin
from django.contrib.auth.models import AnonymousUser
from django.db.models import QuerySet
from django.db.models.expressions import F
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy
from django_admin_display import admin_display
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin
from django_better_admin_arrayfield.models.fields import ArrayField

from shargain.offers.admin.forms import ScrappingTargetAdminForm, TargetAccessForm
from shargain.offers.models import (
    Offer,
    ScrapingCheckin,
    ScrapingUrl,
    ScrappingTarget,
    TargetAccess,
    UserOfferState,
)
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
        "passed_filters",
    )
    list_filter = [
        "target",
        ("closed_at", admin.filters.EmptyFieldListFilter),  # type: ignore
        "passed_filters",
    ]
    readonly_fields = ("passed_filters",)
    ordering = ("-published_at",)
    search_fields = ("title",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(duration=F("closed_at") - F("created_at"))

    @admin_display(short_description=gettext_lazy("Title"), admin_order_field="title")  # type: ignore[arg-type]
    def get_title(self, obj):
        return render_to_string("admin/fields/main_image_offer.html", context={"obj": obj})

    @admin_display(short_description=gettext_lazy("Link to offer"))  # type: ignore[arg-type]
    def get_link(self, obj):
        button_text = _("Go to offer")
        return format_html('<a href="{}" target="_blank">{}</a>', obj.url, button_text)

    @admin_display(
        short_description=gettext_lazy("Closed at"),  # type: ignore[arg-type]
        admin_order_field="closed_at",
    )
    def get_closed_at(self, obj):
        css_class = "btn-outline-danger" if obj.closed_at else "btn-outline-success"
        if obj.closed_at:
            return mark_safe(f"<div class='{css_class}'>{obj.closed_at.strftime('%d-%m-%y %H:%M')}</div>")  # noqa: S308

    @admin_display(
        short_description=gettext_lazy("Duration"),  # type: ignore[arg-type]
        admin_order_field="duration",
    )
    def get_duration(self, obj):
        if obj.closed_at:
            seconds = round((obj.closed_at - obj.created_at).total_seconds())
            return timedelta(seconds=seconds)


class ScrapingUrlInlineAdmin(admin.TabularInline):
    model = ScrapingUrl
    show_change_link = True


class TargetAccessInline(admin.TabularInline):
    model = TargetAccess
    form = TargetAccessForm
    extra = 1
    autocomplete_fields = ("user",)
    fields = ("user", "role", "created_at")
    readonly_fields = ("created_at",)


@admin.register(ScrappingTarget)
class ScrappingTargetAdmin(admin.ModelAdmin, DynamicArrayMixin):
    form = ScrappingTargetAdminForm
    fields = (
        "name",
        "enable_notifications",
        "show_scraping_urls",
        "is_active",
        "notification_config",
        "owner",
        "display_grafana_panel",
    )
    list_display = ("__str__", "owner", "enable_notifications", "is_active")
    search_fields = ("name",)
    readonly_fields = (
        "display_grafana_panel",
        "show_scraping_urls",
    )
    formfield_overrides = {ArrayField: {"widget": AdminDynamicArrayWidget}}
    inlines = [ScrapingUrlInlineAdmin, TargetAccessInline]

    def get_readonly_fields(self, request: HttpRequest, obj: ScrappingTarget | None = None) -> list[str] | tuple:
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj:
            readonly_fields.append("name")
        return readonly_fields

    @admin_display(
        short_description=gettext_lazy("Stats"),  # type: ignore[arg-type]
    )
    def display_grafana_panel(self, obj):
        return render_to_string("admin/grafana_panels.html", context={"obj": obj})

    @admin_display(short_description=_("Urls to scrap"))  # type: ignore[arg-type]
    def show_scraping_urls(self, obj: ScrappingTarget):
        return render_to_string(
            "admin/fields/read_only_urls_to_scrap.html",
            context={"scraping_urls": obj.scrapingurl_set.all()},
        )

    def save_formset(self, request: HttpRequest, form, formset, change: bool):
        instances = formset.save(commit=False)
        for instance in instances:
            if (
                isinstance(instance, TargetAccess)
                and not instance.granted_by_id
                and not isinstance(request.user, AnonymousUser)
            ):
                instance.granted_by = request.user
            instance.save()
        formset.save_m2m()


class StaleUrlFilter(admin.SimpleListFilter):
    title = _("stale urls")
    parameter_name = "stale"

    def lookups(self, request, model_admin):
        return (
            ("stale", _("Stale URLs")),
            ("fresh", _("Fresh URLs")),
        )

    def queryset(self, request, queryset):
        if self.value() == "stale":
            # Default to 24 hours as stale threshold
            stale_threshold = timezone.now() - timedelta(hours=24)
            return queryset.filter(checkins__timestamp__lt=stale_threshold).distinct()
        if self.value() == "fresh":
            stale_threshold = timezone.now() - timedelta(hours=24)
            return queryset.exclude(checkins__timestamp__lt=stale_threshold).distinct()
        return queryset


@admin.register(ScrapingUrl)
class ScrapingUrlAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "scraping_target", "get_scraping_urls", "last_checkin_time")
    list_filter = ("scraping_target", StaleUrlFilter)
    search_fields = ("url",)

    @staticmethod
    def get_scraping_urls(obj: ScrapingUrl) -> str:
        return format_html(
            "<a href={} target=_blank><div style='width:100%'><i class='fas fa-external-link-alt'></i></div></a>",
            obj.url,
        )

    @admin.display(description=_("Last Check-in Time"))
    def last_checkin_time(self, obj):
        """Display the last check-in time for this URL."""
        latest_checkin = obj.checkins.order_by("-timestamp").first()
        if latest_checkin:
            return latest_checkin.timestamp
        return "No check-ins yet"


@admin.register(ScrapingCheckin)
class ScrapingCheckinAdmin(admin.ModelAdmin):
    list_display = ("scraping_url", "get_url", "offers_count", "new_offers_count", "timestamp")
    list_filter = ("scraping_url",)

    @staticmethod
    def get_url(obj: ScrapingCheckin):
        return format_html(
            "<a href={} target=_blank><div style='width:100%'><i class='fas fa-external-link-alt'></i></div></a>",
            obj.scraping_url.url,
        )

    def get_queryset(self, request: HttpRequest) -> QuerySet[ScrapingCheckin]:
        return super().get_queryset(request).select_related("scraping_url")


@admin.register(UserOfferState)
class UserOfferStateAdmin(admin.ModelAdmin):
    list_display = ("user", "offer", "seen_at", "liked_at", "created_at")
    list_filter = ("offer__target",)
    search_fields = ("offer__url", "offer__title", "user__email")
    list_select_related = ("user", "offer")


@admin.register(TargetAccess)
class TargetAccessAdmin(admin.ModelAdmin):
    form = TargetAccessForm
    list_display = ("target", "user", "role", "granted_by", "created_at")
    list_filter = ("role",)
    search_fields = ("target__name", "user__email", "user__username")
    autocomplete_fields = ("target", "user")

    def save_model(self, request: HttpRequest, obj: TargetAccess, form, change: bool):
        if not obj.granted_by_id and not isinstance(request.user, AnonymousUser):
            obj.granted_by = request.user
        super().save_model(request, obj, form, change)
