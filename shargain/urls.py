from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from shargain.notifications.urls import router as notifications_router
from shargain.offers.urls import router as offers_router
from shargain.public_api.api import router as ninja_router

schema_view = get_schema_view(
    openapi.Info(
        title="Shargain API",
        default_version="v1",
        contact=openapi.Contact(email="szymon.sc.cader@gmail.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()

router.registry.extend(offers_router.registry)
router.registry.extend(notifications_router.registry)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/public/", ninja_router.urls),
    path("api/doc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path(
        "api/swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger",
    ),
    path("__debug__/", include("debug_toolbar.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
