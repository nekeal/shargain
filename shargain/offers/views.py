from django_filters import rest_framework as filters
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from shargain.offers.filters import ScrappingTargetFilterSet
from shargain.offers.models import Offer, ScrappingTarget
from shargain.offers.serializers import (
    AddTargetUrlSerializer,
    OfferSerializer,
    ScrappingTargetSerializer,
)
from shargain.offers.services import OfferBatchCreateService


class OfferViewSet(viewsets.ModelViewSet):
    serializer_class = OfferSerializer
    queryset = Offer.objects.all()
    pagination_class = LimitOffsetPagination

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [
                IsAuthenticated(),
            ]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.get_or_create()

    @action(methods=["POST"], detail=False)
    def batch_create(self, request):
        """
        Action which creates non existing offers and sends
        notifications to configured channel.
        """
        new_offers_urls = OfferBatchCreateService({"data": request.data}).run()
        return Response(new_offers_urls)


class ScrappingTargetViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    queryset = ScrappingTarget.objects.filter(is_active=True)
    serializer_class = ScrappingTargetSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ScrappingTargetFilterSet

    def get_serializer_class(self):
        if self.action == "add_target_url":
            return AddTargetUrlSerializer
        return super().get_serializer_class()

    @action(methods=["POST"], detail=True, url_path="add-target-url")
    def add_target_url(self, request, pk=None):
        """
        Action which adds url to existing target
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.get_object()
        obj.url = serializer.validated_data["url"]
        obj.save(update_fields=["url"])
        return Response(ScrappingTargetSerializer(obj).data)
