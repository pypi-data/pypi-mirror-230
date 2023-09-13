from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import json
import pika.exceptions

from kfsd.apps.models.tables.base import BaseModel
from kfsd.apps.core.utils.system import System
from kfsd.apps.core.utils.time import Time
from kfsd.apps.core.msmq.rabbitmq.base import RabbitMQ
from kfsd.apps.core.common.logger import Logger, LogLevel


logger = Logger.getSingleton(__name__, LogLevel.DEBUG)


class Outpost(BaseModel):
    STATUS_CHOICES = (
        ("P", "PENDING"),
        ("I", "IN-PROGRESS"),
        ("E", "ERROR"),
        ("C", "COMPLETED"),
    )

    msg_queue_info = models.JSONField(default=dict)
    msg = models.JSONField(default=dict)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="P")
    attempts = models.IntegerField(default=0)
    debug_info = models.JSONField(default=dict)

    def save(self, *args, **kwargs):
        if not self.identifier:
            self.identifier = System.uuid(32)
        return super().save(*args, **kwargs)

    class Meta:
        app_label = "models"
        verbose_name = "Outpost"
        verbose_name_plural = "Outpost"


@receiver(post_save, sender=Outpost)
def signal_send_msg(sender, instance, created, **kwargs):
    if created:
        send_msg(instance)


def log_error(instance):
    oldDebugInfo = instance.debug_info
    currentTimeStr = Time.calculate_time(Time.current_time(), {"minutes": 0}, True)
    oldDebugInfo[currentTimeStr] = "Error occurred in publishing outpost msg"
    instance.debug_info = oldDebugInfo
    instance.attempts += 1
    instance.status = "E"
    instance.save()


def send_msg(instance):
    logger.info(
        "Sending msg to MSMQ for outpost id: {}, msmq: {}, msg: {}".format(
            instance.identifier,
            json.dumps(instance.msg_queue_info, indent=4),
            json.dumps(instance.msg, indent=4),
        )
    )
    try:
        configId = System.getEnv("service_id")
        rabbitMQ = RabbitMQ.getSingleton(configId)
        if rabbitMQ.isMQMQEnabled():
            rabbitMQ.publish(instance.msg_queue_info, json.dumps(instance.msg))
        else:
            logger.info(
                "Sending msg to MSMQ for outpost id: {} failed, reason: MSMQ is disabled, check your settings 'services.rabbitmq.is_enabled'".format(
                    instance.identifier
                )
            )
        instance.delete()
    except pika.exceptions.StreamLostError as e:
        logger.error("Recd error on publish: {}".format(e.__str__()))
        log_error(instance)
    except Exception as e:
        logger.error("Recd error on publish: {}".format(e.__str__()))
        log_error(instance)
