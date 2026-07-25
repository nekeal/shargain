from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class OffersConfig(AppConfig):
    name = "shargain.offers"
    verbose_name = _("Offers")

    def ready(self):
        from shargain.offers.services.offer_field_resolver import OfferFieldResolver
        from shargain.offers.services.source_plugins import registered_plugins

        for plugin in registered_plugins:
            OfferFieldResolver.register(plugin)
