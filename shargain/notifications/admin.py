from typing import List

from django.contrib import admin
from django.urls import URLPattern, path

from shargain.notifications.models import NotificationConfig
from shargain.notifications.views.admin import SendTestNotificationView


@admin.register(NotificationConfig)
class NotificationConfigAdmin(admin.ModelAdmin):
    list_display = ("name", "channel")
    exclude = ("_token",)

    def get_urls(self) -> List[URLPattern]:
        urls = super().get_urls()
        urls.insert(
            0,
            path(
                "<int:object_id>/test-notification/",
                SendTestNotificationView.as_view(),
                name="notifications_notificationconfig_test_notification",
            ),
        )
        return urls
