from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView
from rest_framework import routers

from kfsd.apps.endpoints.views.common.exchange import ExchangeModelViewSet
from kfsd.apps.endpoints.views.common.queue import QueueModelViewSet
from kfsd.apps.endpoints.views.common.route import RouteModelViewSet
from kfsd.apps.endpoints.views.common.producer import ProducerModelViewSet

from kfsd.apps.endpoints.views.utils.utils import UtilsViewSet
from kfsd.apps.endpoints.views.utils.common import CommonViewSet
from kfsd.apps.endpoints.views.common.outpost import OutpostModelViewSet

router = routers.DefaultRouter()
router.include_format_suffixes = False

router.register("exchange", ExchangeModelViewSet, basename="exchange")
router.register("queue", QueueModelViewSet, basename="queue")
router.register("route", RouteModelViewSet, basename="route")
router.register("producer", ProducerModelViewSet, basename="producer")

router.register("utils", UtilsViewSet, basename="utils")
router.register("common", CommonViewSet, basename="common")
router.register("outpost", OutpostModelViewSet, basename="outpost")

urlpatterns = [
    path("", include(router.urls)),
    path("schema/", SpectacularAPIView.as_view(), name="schema-api"),
]
