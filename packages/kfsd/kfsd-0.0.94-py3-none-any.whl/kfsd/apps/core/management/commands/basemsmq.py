from django.core.management.base import BaseCommand
from kfsd.apps.core.msmq.rabbitmq.base import RabbitMQ
from kfsd.apps.core.utils.time import Time
from kfsd.apps.endpoints.serializers.common.outpost import MsgSerializer

from kfsd.apps.core.common.logger import Logger, LogLevel
from kfsd.apps.core.utils.dict import DictUtils
from kfsd.apps.models.tables.outpost import Outpost, send_msg
from kfsd.apps.models.constants import INBOUND_SIGNAL_CLEAR_OUTPOST


import json

logger = Logger.getSingleton(__name__, LogLevel.DEBUG)


def clear_outpost(data):
    outpostQS = Outpost.objects.filter(status="E").order_by("created")
    identifiers = [outpost.identifier for outpost in outpostQS]
    logger.info(
        "Recd CLEAR_OUTPOST command on msmq, identifiers: {} with 'Error' status found.".format(
            identifiers if identifiers else None
        )
    )
    for outpostIns in outpostQS:
        send_msg(outpostIns)


callback_map = {INBOUND_SIGNAL_CLEAR_OUTPOST: clear_outpost}


def base_callback(ch, method, properties, body):
    bodyStr = body.decode().replace("'", '"')
    jsonStr = json.loads(bodyStr)
    serializedData = MsgSerializer(data=jsonStr)
    serializedData.is_valid(raise_exception=True)

    action = DictUtils.get(serializedData.data, "action")
    if action in callback_map:
        callback_map[action](serializedData.data)
    else:
        logger.error("Action : {} not handled in message consumption".format(action))


class Command(BaseCommand):
    help = "Listens to a RabbitMQ topic"

    def __init__(self, callbackFn=base_callback):
        self.__callbackFn = callbackFn

    def add_arguments(self, parser):
        parser.add_argument(
            "-s",
            "--service_config_id",
            type=str,
            help="Service Config Id",
        )

    def connectToMSMQ(self, serviceConfigId):
        try:
            msmqHandler = RabbitMQ.getSingleton(serviceConfigId)
            return msmqHandler
        except Exception as e:
            print(e)
            logger.error(
                "Error connecting to RabbitMQ, check if RabbitMQ instance is up!"
            )
            Time.sleep(30)
            self.connectToMSMQ()

    def handle(self, *args, **options):
        logger.info("Listening to MSMQ messages...")
        serviceConfigId = DictUtils.get(options, "service_config_id")
        msmqHandler = self.connectToMSMQ(serviceConfigId)
        if msmqHandler.isMQMQEnabled():
            msmqHandler.consumeQueues(self.__callbackFn)
            msmqHandler.startConsuming()
        else:
            logger.info("MSMQ is disabled")
