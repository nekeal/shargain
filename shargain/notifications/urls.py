from typing import Any, List

from rest_framework.routers import DefaultRouter

from shargain.notifications.telegram.utils import get_token_for_webhook_url
from shargain.notifications.views.api import (
    NotificationConfigViewSet,
    TelegramWebhookViewSet,
)

router = DefaultRouter()

router.register("notification-configs", NotificationConfigViewSet)
router.register(
    f"webhooks/telegram/{get_token_for_webhook_url()}/",
    TelegramWebhookViewSet,
    basename="webhook",
)

urlpatterns: List[Any] = []
