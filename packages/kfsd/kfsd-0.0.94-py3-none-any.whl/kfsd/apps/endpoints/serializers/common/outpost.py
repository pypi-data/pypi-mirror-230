from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.core.validators import (
    MinLengthValidator,
    MaxLengthValidator,
    RegexValidator,
)

from kfsd.apps.models.tables.outpost import Outpost
from kfsd.apps.endpoints.serializers.common.model import BaseModelSerializer
from kfsd.apps.models.constants import MAX_LENGTH, MIN_LENGTH, MSMQ_NAME_REGEX_CONDITION


class MsgQueueSerializer(serializers.Serializer):
    exchange = serializers.CharField(
        validators=[
            MinLengthValidator(MIN_LENGTH),
            MaxLengthValidator(MAX_LENGTH),
            RegexValidator(
                MSMQ_NAME_REGEX_CONDITION,
                message=_(
                    "exchange name has to match {}".format(MSMQ_NAME_REGEX_CONDITION)
                ),
                code="exchange_invalid_name",
            ),
        ]
    )
    routing_key = serializers.CharField(required=False, allow_blank=True)
    properties = serializers.JSONField(default=dict)


class MsgSerializer(serializers.Serializer):
    action = serializers.CharField(
        validators=[
            MinLengthValidator(MIN_LENGTH),
            MaxLengthValidator(MAX_LENGTH),
            RegexValidator(
                MSMQ_NAME_REGEX_CONDITION,
                message=_(
                    "action name has to match {}".format(MSMQ_NAME_REGEX_CONDITION)
                ),
                code="action_invalid_name",
            ),
        ],
        required=True,
    )
    target_model = serializers.CharField(required=False)
    data = serializers.JSONField(default=dict)


class OutpostModelSerializer(BaseModelSerializer):
    msg_queue_info = MsgQueueSerializer()
    msg = MsgSerializer()
    status = serializers.ChoiceField(
        choices=["PENDING", "IN-PROGRESS", "ERROR", "COMPLETED"], default="IN-PROGRESS"
    )
    attempts = serializers.IntegerField(default=0)
    debug_info = serializers.JSONField(default=dict, read_only=True)

    class Meta:
        model = Outpost
        fields = "__all__"


class OutpostViewModelSerializer(OutpostModelSerializer):
    id = None
    created = None
    updated = None

    class Meta:
        model = Outpost
        exclude = ("created", "updated", "id")
