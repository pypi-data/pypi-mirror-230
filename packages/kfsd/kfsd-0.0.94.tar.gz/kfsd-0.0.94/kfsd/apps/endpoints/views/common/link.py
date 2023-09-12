from drf_spectacular.utils import extend_schema_view

from kfsd.apps.endpoints.views.common.custom_model import CustomModelViewSet
from kfsd.apps.models.tables.link import Link
from kfsd.apps.endpoints.serializers.common.link import LinkViewModelSerializer
from kfsd.apps.endpoints.views.docs.link import LinkDoc


@extend_schema_view(**LinkDoc.modelviewset())
class LinkModelViewSet(CustomModelViewSet):
    queryset = Link.objects.all()
    serializer_class = LinkViewModelSerializer
