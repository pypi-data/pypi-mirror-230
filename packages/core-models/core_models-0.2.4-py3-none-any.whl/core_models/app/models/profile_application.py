from django.contrib.postgres.fields import ArrayField
from django.db import models
from model_utils import FieldTracker

from . import User, Company, CompanyIncorporation
from .sector import Sector
from .country import Country
from .base import BaseModelAbstract
from .. import notification_manager
from ... import constants, utils


class ProfileApplication(BaseModelAbstract, models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    company_registration_number = models.CharField(max_length=50)
    company_incorporation = models.OneToOneField(
        CompanyIncorporation, models.CASCADE, null=True, blank=True
    )
    email = models.EmailField(unique=False, null=False, blank=False)
    phone_number = models.CharField(max_length=25)
    country = models.ForeignKey(
        Country, models.SET_NULL, null=True, blank=True
    )
    sector = models.ForeignKey(Sector, models.SET_NULL, null=True, blank=True)
    oecd_buyers = ArrayField(
        ArrayField(
            models.CharField(max_length=255),
            size=2
        )
    )
    non_oecd_buyers = ArrayField(
        ArrayField(
            models.CharField(max_length=255),
            size=2
        ),
        null=True, blank=True
    )
    annual_turnover = models.DecimalField(
        decimal_places=2, max_digits=30,
        null=False, blank=False
    )
    status = models.CharField(
        max_length=1,
        choices=constants.PROFILE_REQUEST_STATUSES,
        default=constants.PENDING_PROFILE_STATUS
    )
    rejection_reason = models.TextField(null=True, blank=True)
    tracker = FieldTracker(fields=['status'])

    def __unicode__(self):
        return self.company_name

    @property
    def approved(self) -> bool:
        return self.status == constants.APPROVED_PROFILE_STATUS

    def save(self, keep_deleted=False, **kwargs):
        status_changed = self.tracker.has_changed('status') or not self.id
        super(ProfileApplication, self).save(keep_deleted, **kwargs)
        if status_changed:
            if self.status == constants.APPROVED_PROFILE_STATUS:
                pwd = utils.random_string(8)
                notification_manager.profile_application_notification(self, pwd)
                user, created = User.objects.get_or_create(
                    email=self.email,
                    defaults={
                        "first_name": self.first_name,
                        "last_name": self.last_name,
                        "user_type": constants.SELLER_USER_TYPE,
                        "phone_number": self.phone_number,
                        "email_verified": True,
                        "change_password": True
                    }
                )
                if created:
                    user.set_password(pwd)
                    user.save()
                    company, created2 = Company.objects.get_or_create(
                        user=user,
                        defaults={
                            "name": self.company_name,
                            "registration_number":
                                self.company_registration_number,
                            "sector": self.sector,
                            "country": self.country,
                            "annual_turnover": self.annual_turnover,
                        }
                    )
                else:
                    company = user.company
                if self.company_incorporation:
                    self.company_incorporation.company = company
                    self.company_incorporation.team_chart = company
                    self.company_incorporation.team_chart.save()
                    self.company_incorporation.save()
            else:
                notification_manager.profile_application_notification(self)
