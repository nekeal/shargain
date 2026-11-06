from django.contrib import admin

from shargain.jobs.models import Job, RateLimit


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "stream_key", "status", "attempts", "visible_at", "created_at")
    list_filter = ("type", "status")
    search_fields = ("stream_key", "type", "dedup_key")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(RateLimit)
class RateLimitAdmin(admin.ModelAdmin):
    list_display = ("key", "tokens", "blocked_until", "updated_at")
    search_fields = ("key",)
