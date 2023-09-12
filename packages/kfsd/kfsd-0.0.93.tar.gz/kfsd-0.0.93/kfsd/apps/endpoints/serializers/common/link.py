from rest_framework import serializers
from django.core.validators import (
    MinLengthValidator,
)

from kfsd.apps.models.constants import MIN_LENGTH
from kfsd.apps.endpoints.serializers.common.model import BaseModelSerializer
from kfsd.apps.models.tables.link import Link
from kfsd.apps.models.tables.platform import Platform


class LinkModelSerializer(BaseModelSerializer):
    link = serializers.CharField(
        validators=[
            MinLengthValidator(MIN_LENGTH),
        ]
    )
    platform = serializers.SlugRelatedField(
        required=False,
        many=False,
        read_only=False,
        slug_field="identifier",
        queryset=Platform.objects.all(),
    )
    link_id = serializers.CharField(read_only=True)

    class Meta:
        model = Link
        fields = "__all__"


class LinkViewModelSerializer(BaseModelSerializer):
    id = None
    created = None
    updated = None

    class Meta:
        model = Link
        exclude = ("created", "updated", "id")
