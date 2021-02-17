from rest_framework.routers import DefaultRouter

from shargain.offers.views import OfferViewSet

router = DefaultRouter()

router.register("offers", OfferViewSet)
