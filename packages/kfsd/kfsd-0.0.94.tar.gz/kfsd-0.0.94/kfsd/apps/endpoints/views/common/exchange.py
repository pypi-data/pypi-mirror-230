from kfsd.apps.endpoints.views.common.custom_model import CustomModelViewSet
from kfsd.apps.models.tables.exchange import Exchange
from kfsd.apps.endpoints.serializers.common.exchange import ExchangeViewModelSerializer


class ExchangeModelViewSet(CustomModelViewSet):
    queryset = Exchange.objects.all()
    serializer_class = ExchangeViewModelSerializer
