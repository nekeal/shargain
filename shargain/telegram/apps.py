from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TelegramConfig(AppConfig):
    name = "shargain.telegram"
    verbose_name = _("Telegram")
    _TELEGRAM_INITIALIZED = False

    def ready(self):
        if not self.__class__._TELEGRAM_INITIALIZED:
            from . import add_link_flow, detect_list_url  # noqa: F401

            self.__class__._TELEGRAM_INITIALIZED = True
