from django_filters import rest_framework as filters
from rest_framework import viewsets

from shargain.notifications.models import NotificationConfig
from shargain.notifications.serializers import NotificationConfigSerializer


class NotificationConfigViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NotificationConfig.objects.all()
    serializer_class = NotificationConfigSerializer
    filter_backends = (filters.DjangoFilterBackend,)
