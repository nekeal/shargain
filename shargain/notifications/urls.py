from typing import Any, List

from rest_framework.routers import DefaultRouter

from shargain.notifications.views import NotificationConfigViewSet

router = DefaultRouter()

router.register("notification-configs", NotificationConfigViewSet)

urlpatterns: List[Any] = []
