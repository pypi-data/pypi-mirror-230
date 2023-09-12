from kfsd.apps.endpoints.views.common.custom_model import CustomModelViewSet
from kfsd.apps.models.tables.queue import Queue
from kfsd.apps.endpoints.serializers.common.queue import QueueViewModelSerializer


class QueueModelViewSet(CustomModelViewSet):
    queryset = Queue.objects.all()
    serializer_class = QueueViewModelSerializer
