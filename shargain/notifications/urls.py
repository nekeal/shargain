from typing import Any

from rest_framework.routers import DefaultRouter

from shargain.notifications.views.api import (
    NotificationConfigViewSet,
    TelegramWebhookViewSet,
)
from shargain.telegram.bot import get_token_for_webhook_url

router = DefaultRouter()

router.register("notification-configs", NotificationConfigViewSet)
router.register(
    f"webhooks/telegram/{get_token_for_webhook_url()}",
    TelegramWebhookViewSet,
    basename="webhook",
)

urlpatterns: list[Any] = []
