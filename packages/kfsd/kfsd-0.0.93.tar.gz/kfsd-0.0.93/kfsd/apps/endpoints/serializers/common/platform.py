from rest_framework import serializers
from django.core.validators import (
    MinLengthValidator,
    MaxLengthValidator,
)

from kfsd.apps.models.constants import MAX_LENGTH, MIN_LENGTH
from kfsd.apps.endpoints.serializers.common.model import BaseModelSerializer
from kfsd.apps.models.tables.platform import Platform


class PlatformModelSerializer(BaseModelSerializer):
    name = serializers.CharField(
        validators=[
            MinLengthValidator(MIN_LENGTH),
            MaxLengthValidator(MAX_LENGTH),
        ]
    )
    type = serializers.CharField(
        validators=[
            MinLengthValidator(MIN_LENGTH),
            MaxLengthValidator(MAX_LENGTH),
        ]
    )
    slug = serializers.SlugField(required=False)

    class Meta:
        model = Platform
        fields = "__all__"


class PlatformViewModelSerializer(BaseModelSerializer):
    id = None
    created = None
    updated = None

    class Meta:
        model = Platform
        exclude = ("created", "updated", "id")
