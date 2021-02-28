from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from shargain.offers.models import Offer, ScrappingTarget
from shargain.offers.serializers import OfferSerializer, ScrappingTargetSerializer
from shargain.offers.services import OfferBatchCreateService


class OfferViewSet(viewsets.ModelViewSet):
    serializer_class = OfferSerializer
    queryset = Offer.objects.all()

    def perform_create(self, serializer):
        serializer.get_or_create()

    @action(methods=["POST"], detail=False)
    def batch_create(self, request):
        """
        Action which creates non existing offers and sends
        notifications to configured channel.
        """
        new_offers_urls = OfferBatchCreateService(dict(data=request.data)).run()
        return Response(new_offers_urls)


class ScrappingTargetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ScrappingTarget.objects.all()
    serializer_class = ScrappingTargetSerializer
