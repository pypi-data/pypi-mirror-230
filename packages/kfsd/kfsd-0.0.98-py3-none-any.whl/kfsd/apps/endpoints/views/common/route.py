from kfsd.apps.endpoints.views.common.custom_model import CustomModelViewSet
from kfsd.apps.models.tables.route import Route
from kfsd.apps.endpoints.serializers.common.route import RouteViewModelSerializer


class RouteModelViewSet(CustomModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteViewModelSerializer
