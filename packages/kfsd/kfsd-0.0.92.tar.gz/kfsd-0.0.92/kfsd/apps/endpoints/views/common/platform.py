from drf_spectacular.utils import extend_schema_view

from kfsd.apps.endpoints.views.common.custom_model import CustomModelViewSet
from kfsd.apps.models.tables.platform import Platform
from kfsd.apps.endpoints.serializers.common.platform import PlatformViewModelSerializer
from kfsd.apps.endpoints.views.docs.platform import PlatformDoc


@extend_schema_view(**PlatformDoc.modelviewset())
class PlatformModelViewSet(CustomModelViewSet):
    queryset = Platform.objects.all()
    serializer_class = PlatformViewModelSerializer
