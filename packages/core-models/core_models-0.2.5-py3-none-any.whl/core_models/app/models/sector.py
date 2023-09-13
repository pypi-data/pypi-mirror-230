from django.db import models

from .base import BaseModelAbstract


class Sector(BaseModelAbstract, models.Model):
    name = models.CharField(
        max_length=100, unique=True,
        null=False, blank=False
    )

    def __unicode__(self):
        return self.name
