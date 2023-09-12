from django.db import models

from kfsd.apps.core.utils.system import System
from kfsd.apps.models.constants import MAX_LENGTH
from kfsd.apps.models.tables.base import BaseModel
from kfsd.apps.models.tables.platform import Platform


# Github, Twitter, Linkedin, Youtube, Website
class Link(BaseModel):
    link = models.TextField()
    platform = models.ForeignKey(
        Platform, on_delete=models.CASCADE, null=True, blank=True
    )
    link_id = models.CharField(max_length=MAX_LENGTH)

    def save(self, *args, **kwargs):
        self.uniq_id = System.api_key(6)
        if self.platform:
            self.identifier = "{},LINK_ID={}".format(
                self.platform.identifier, self.link_id
            )
        else:
            self.identifier = "LINK_ID={}".format(self.link_id)
        return super().save(*args, **kwargs)

    class Meta:
        app_label = "models"
        verbose_name = "Link"
        verbose_name_plural = "Link"
