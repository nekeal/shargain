from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class QuotasConfig(AppConfig):
    name = "shargain.quotas"
    verbose_name = _("Quotas")

    def ready(self):
        from . import signals  # noqa: F401
