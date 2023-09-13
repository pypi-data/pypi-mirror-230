from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer
from rest_framework.views import Response

from kfsd.apps.models.tables.outpost import Outpost, send_msg
from kfsd.apps.endpoints.serializers.common.outpost import OutpostViewModelSerializer
from kfsd.apps.endpoints.views.docs.outpost import OutpostDoc
from kfsd.apps.endpoints.views.common.custom_model import CustomModelViewSet


@extend_schema_view(**OutpostDoc.modelviewset())
class OutpostModelViewSet(CustomModelViewSet):
    queryset = Outpost.objects.all()
    serializer_class = OutpostViewModelSerializer

    @extend_schema(**OutpostDoc.send_all_view())
    @action(
        detail=False,
        methods=["get"],
        renderer_classes=[JSONRenderer],
        url_path="send/all",
    )
    def send_all(self, request, *args, **kwargs):
        queryset = Outpost.objects.all()
        for obj in queryset:
            send_msg.delay(obj.id)
        return Response({"detail": "ok"})
