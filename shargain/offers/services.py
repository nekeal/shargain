from typing import List, Tuple

from shargain.notifications.services.notifications import NewOfferNotificationService
from shargain.offers.models import Offer
from shargain.offers.serializers import OfferBatchCreateSerializer


class OfferBatchCreateService:
    serializer_class = OfferBatchCreateSerializer
    notification_service_class = NewOfferNotificationService

    def __init__(self, serializer_kwargs: dict, notify: bool = True):
        self._serializer_kwargs = serializer_kwargs

    def run(self):
        serializer = self.serializer_class(**self._serializer_kwargs)
        serializer.is_valid(raise_exception=True)
        offers: List[Tuple[Offer, bool]] = self.create(serializer.validated_data)
        new_offers = list(map(lambda r: r[0], filter(lambda x: x[1], offers)))
        self._notify(new_offers, serializer.validated_data["target"])
        return [offer.url for offer in new_offers]

    @staticmethod
    def simplify_url(url):  # currently not used
        if "olx.pl" in url:
            return url.rsplit("#")[0]
        return url

    def create(self, validated_data) -> List[Tuple[Offer, bool]]:
        offers: List[Tuple[Offer, bool]] = []
        for offer_data in validated_data["offers"]:
            offer_url = offer_data.pop("url")
            try:
                offer, created = Offer.objects.get_or_create(
                    url=offer_url,
                    target=validated_data["target"],
                    defaults=offer_data,
                )
            except Offer.MultipleObjectsReturned:
                offer, created = (
                    Offer.objects.filter(url=offer_url, target=validated_data["target"]).first(),
                    False,
                )
            offers.append((offer, created))
        return offers

    def _notify(self, new_offers, scrapping_target):
        if new_offers and scrapping_target.notification_config and scrapping_target.enable_notifications:
            self.notification_service_class(new_offers, scrapping_target).run()
