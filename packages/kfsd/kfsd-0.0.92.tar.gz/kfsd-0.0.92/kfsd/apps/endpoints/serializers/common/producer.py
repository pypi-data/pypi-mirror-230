from rest_framework import serializers
from django.core.validators import (
    MinLengthValidator,
    MaxLengthValidator,
)

from kfsd.apps.endpoints.serializers.common.model import BaseModelSerializer
from kfsd.apps.models.tables.route import Route
from kfsd.apps.models.tables.producer import Producer
from kfsd.apps.models.constants import MAX_LENGTH, MIN_LENGTH


class ProducerModelSerializer(BaseModelSerializer):
    signal = serializers.CharField(
        validators=[
            MinLengthValidator(MIN_LENGTH),
            MaxLengthValidator(MAX_LENGTH),
        ],
    )
    route = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field="identifier",
        queryset=Route.objects.all(),
    )
    properties = serializers.JSONField(default=dict)

    class Meta:
        model = Producer
        fields = "__all__"


class ProducerViewModelSerializer(ProducerModelSerializer):
    id = None
    created = None
    updated = None

    class Meta:
        model = Producer
        exclude = ("created", "updated", "id")
