from rest_framework.routers import DefaultRouter

from shargain.offers.views import OfferViewSet, ScrappingTargetViewSet

router = DefaultRouter()

router.register("offers", OfferViewSet)
router.register("scrapping-targets", ScrappingTargetViewSet)
