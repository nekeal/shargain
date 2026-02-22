from django.contrib import admin

from shargain.subscriptions.models import Plan, UserSubscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "max_urls", "max_offers_per_target", "is_default", "is_active", "display_order")
    list_filter = ("is_default", "is_active")
    search_fields = ("name", "slug")


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "started_at", "expires_at", "is_active")
    list_filter = ("is_active", "plan")
    search_fields = ("user__username", "user__email", "plan__name", "plan__slug")
