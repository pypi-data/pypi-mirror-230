from django.db import models

from .sector import Sector
from .country import Country
from .base import BaseModelAbstract
from .user import User


class UserConfiguration(BaseModelAbstract, models.Model):
    created_by = None
    user = models.OneToOneField(User, models.CASCADE, related_name='config')
    countries = models.ManyToManyField(Country, null=True, blank=True)
    sectors = models.ManyToManyField(Sector, null=True, blank=True)
    maturity = models.IntegerField(default=0)
    discount_range = models.JSONField(default=list([1, 50]))
