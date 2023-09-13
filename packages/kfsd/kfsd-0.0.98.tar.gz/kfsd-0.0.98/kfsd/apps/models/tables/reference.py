from django.db import models

from kfsd.apps.models.constants import MAX_LENGTH
from kfsd.apps.models.tables.base import BaseModel


# Github, Twitter, Linkedin, Youtube, Website
class Reference(BaseModel):
    type = models.CharField(max_length=MAX_LENGTH)
    attrs = models.JSONField(default=dict)

    class Meta:
        app_label = "models"
        verbose_name = "Reference"
        verbose_name_plural = "References"
