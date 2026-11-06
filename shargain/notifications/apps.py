from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    name = "shargain.notifications"

    def ready(self):
        from . import job_handlers  # noqa: F401
