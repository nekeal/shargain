from rest_framework import serializers

from shargain.notifications.models import NotificationConfig


class NotificationConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationConfig
        fields = ("id", "name", "channel")
