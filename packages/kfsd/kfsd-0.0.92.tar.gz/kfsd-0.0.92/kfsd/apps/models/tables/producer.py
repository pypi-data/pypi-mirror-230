from django.db import models

from kfsd.apps.models.constants import MAX_LENGTH
from kfsd.apps.models.tables.base import BaseModel
from kfsd.apps.models.tables.route import Route


class Producer(BaseModel):
    signal = models.CharField(max_length=MAX_LENGTH)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    properties = models.JSONField(default=dict)

    def save(self, *args, **kwargs):
        self.identifier = "{}={}".format("SIGNAL", self.action)
        return super().save(*args, **kwargs)

    class Meta:
        app_label = "models"
        verbose_name = "Route"
        verbose_name_plural = "Routes"
