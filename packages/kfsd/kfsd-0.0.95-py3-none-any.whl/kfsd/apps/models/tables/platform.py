from django.db import models
from django.utils.text import slugify

from kfsd.apps.models.constants import MAX_LENGTH
from kfsd.apps.models.tables.base import BaseModel


# Github, Twitter, Linkedin, Youtube, Website
class Platform(BaseModel):
    name = models.CharField(max_length=MAX_LENGTH)
    type = models.CharField(max_length=MAX_LENGTH)
    slug = models.SlugField()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        self.identifier = "TYPE={},PLATFORM={}".format(self.type, self.name)
        return super().save(*args, **kwargs)

    class Meta:
        app_label = "models"
        verbose_name = "Platform"
        verbose_name_plural = "Platform"
