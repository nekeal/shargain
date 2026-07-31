from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class OffersConfig(AppConfig):
    name = "shargain.offers"
    verbose_name = _("Offers")

    def ready(self):
        from shargain.offers.field_extraction import OfferFieldResolver, registered_plugins

        for plugin in registered_plugins:
            OfferFieldResolver.register(plugin)
