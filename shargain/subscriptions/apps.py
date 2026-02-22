from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SubscriptionsConfig(AppConfig):
    name = "shargain.subscriptions"
    verbose_name = _("Subscriptions")

    def ready(self):
        from . import signals  # noqa: F401
