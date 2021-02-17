from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from shargain.offers.urls import router as offers_router

router = DefaultRouter()

router.registry.extend(offers_router.registry)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]
