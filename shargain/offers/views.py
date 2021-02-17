from rest_framework import viewsets

from shargain.offers.models import Offer
from shargain.offers.serializers import OfferSerializer


class OfferViewSet(viewsets.ModelViewSet):
    serializer_class = OfferSerializer
    queryset = Offer.objects.all()
