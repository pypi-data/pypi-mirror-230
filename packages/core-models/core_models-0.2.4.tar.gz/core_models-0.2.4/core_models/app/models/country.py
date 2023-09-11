from cities_light.abstract_models import (AbstractCity, AbstractRegion,
                                          AbstractSubRegion, AbstractCountry)
from cities_light.receivers import connect_default_signals
from django.db import models


class Country(AbstractCountry):
    active = models.BooleanField(default=False)
    oecd = models.BooleanField(default=False)


class Region(AbstractRegion):
    pass


class SubRegion(AbstractSubRegion):
    pass


class City(AbstractCity):
    modification_date = models.CharField(max_length=40)


connect_default_signals(Country)
connect_default_signals(Region)
connect_default_signals(SubRegion)
connect_default_signals(City)
