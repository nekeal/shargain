from django_filters import rest_framework as filters
from rest_framework import mixins, viewsets
from rest_framework.response import Response
from telebot.types import Update

from shargain.notifications.models import NotificationConfig
from shargain.notifications.serializers import NotificationConfigSerializer
from shargain.telegram.bot import TelegramBot


class NotificationConfigViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NotificationConfig.objects.all()
    serializer_class = NotificationConfigSerializer
    filter_backends = (filters.DjangoFilterBackend,)


class TelegramWebhookViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    def create(self, request, *args, **kwargs):
        update = Update.de_json(request.data)

        TelegramBot.get_bot().process_new_updates([update])
        return Response({"ok": True})
