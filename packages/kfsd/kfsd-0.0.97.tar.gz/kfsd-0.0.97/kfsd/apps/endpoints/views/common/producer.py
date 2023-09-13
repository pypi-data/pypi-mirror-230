from kfsd.apps.endpoints.views.common.custom_model import CustomModelViewSet
from kfsd.apps.models.tables.producer import Producer
from kfsd.apps.endpoints.serializers.common.producer import ProducerViewModelSerializer


class ProducerModelViewSet(CustomModelViewSet):
    queryset = Producer.objects.all()
    serializer_class = ProducerViewModelSerializer
