import os

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone

from .currency import Currency
from .sector import Sector
from .country import Country, Region, City
from .base import BaseModelAbstract
from .user import User


def team_chart_upload_to(_):
    pass

def receivables_and_payables_upload_to(_):
    pass


class Company(BaseModelAbstract, models.Model):
    created_by = None
    user = models.OneToOneField(User, models.CASCADE, related_name='company')
    name = models.CharField(max_length=255)
    sector = models.ForeignKey(Sector, models.SET_NULL, null=True, blank=True)
    registration_number = models.CharField(max_length=100, null=True, blank=True)
    annual_turnover = models.DecimalField(decimal_places=2, max_digits=30, null=True, blank=True)
    address_line1 = models.TextField(null=True, blank=True)
    address_line2 = models.TextField(null=True, blank=True)
    postcode = models.CharField(max_length=100, null=True, blank=True)
    country = models.ForeignKey(Country, models.SET_NULL, blank=True, null=True)
    region = models.ForeignKey(Region, models.SET_NULL, blank=True, null=True, verbose_name="Region/State")
    city = models.ForeignKey(City, models.SET_NULL, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    date_verified = models.DateTimeField(null=True, blank=True)

    @property
    def address(self):
        return f"{self.address_line1}, {self.city}, {self.region}, {self.country}"

    class Meta:
        verbose_name_plural = 'Companies'

    def save(self, keep_deleted=False, **kwargs):
        self.date_verified = timezone.now() if self.is_verified else None
        super(Company, self).save(keep_deleted, **kwargs)

    def __unicode__(self):
        return f"{self.name}|{self.registration_number}|{self.is_verified}"


def doc_upload_to(instance, filename):
    f, ext = os.path.splitext(filename)
    return f'company-docs/{instance.id}{ext}'


class CompanyDocument(BaseModelAbstract, models.Model):
    company = models.ForeignKey(Company, models.CASCADE, null=True,
                                blank=True, related_name='docs')
    file = models.FileField(null=False, blank=False, upload_to=doc_upload_to)
    name = models.CharField(max_length=255, null=False, blank=False)

    class Meta:
        verbose_name = "Company Document"
        verbose_name_plural = "Company Documents"

    def __unicode__(self):
        if not self.company:
            return self.name
        return f"{self.company.name} - {self.name}"


class CompanyIncorporation(BaseModelAbstract, models.Model):
    company = models.OneToOneField(
        Company, models.CASCADE, null=True, blank=True,
        related_name='incorporation_information'
    )
    website = models.URLField(null=False, blank=False)
    external_auditors = ArrayField(
        models.CharField(max_length=255),
        null=False, blank=False
    )
    directors = ArrayField(
        models.CharField(max_length=255),
        null=False, blank=False
    )
    document = models.ForeignKey(
        CompanyDocument, models.DO_NOTHING,
        null=True, blank=True,
        related_name="incorporation_information"
    )
    parent_company = models.CharField(
        max_length=255,
        help_text='Full Legal Corporate Name of Parent Company'
    )
    trading_entity = models.CharField(
        max_length=255,
        help_text='Full legal Corporate Name of Trading Entity (if different)'
    )

    def __unicode__(self):
        if self.company is None:
            return 'Company Incorporation'
        return f"{self.company.name}"


class CommercialInformation(BaseModelAbstract, models.Model):
    company = models.OneToOneField(
        Company, models.CASCADE, related_name='commercial_information'
    )
    annual_export_vs_domestic = models.FloatField(
        help_text="What percentage of the business’s annual sales/turnover "
                  "is from exports versus domestic sales?",
    )
    monthly_exports = models.DecimalField(
        decimal_places=2,
        max_digits=30,
        help_text="What is the value of your exports monthly?",
    )
    major_currency = models.ForeignKey(
        Currency, models.DO_NOTHING,
        null=False, blank=False,
        help_text="In what currency is the majority of your sales denominated in?"
    )
    financing_payment_terms = ArrayField(
        models.CharField(max_length=100),
        help_text="What are the main types of financing your company uses "
                  "(e.g unsecured loans..etc) and what are the payment terms?",
        null=True, blank=True
    )
    finance_providers = ArrayField(
        models.CharField(max_length=100),
        help_text="Who are your current predominant finance providers?",
        null=True, blank=True
    )
    avg_interest_rate = models.FloatField(
        default=0,
        help_text="What is the current avg. interest rate that your company "
                  "pays for short-term debt (how much are you currently "
                  "paying in interest)?",
    )
    monthly_finance_needed = models.DecimalField(
        default=0,
        decimal_places=2, max_digits=30,
        help_text="How much financing do you need on a monthly basis?",
    )
    accounting_software = ArrayField(
        models.CharField(max_length=100),
        null=False, blank=False,
        help_text="Does your company use any accounting software? "
                  "If so, what is the name of the software and provider?",
    )
    document = models.ForeignKey(
        CompanyDocument, models.DO_NOTHING,
        null=True, blank=True,
        related_name="commercial_information"
    )
    # receivables_and_payables = models.ForeignKey(
    #     CompanyDocument, models.DO_NOTHING,
    #     null=False, blank=False,
    #     help_text="Monthly Receivables & Payables Aging book for last 12 months",
    #     related_name="receivables_and_payables"
    # )
    # sales_ledger = models.ForeignKey(
    #     CompanyDocument, models.DO_NOTHING,
    #     null=False, blank=False,
    #     help_text="Current Open Sales Ledger",
    #     related_name="sales_ledger"
    # )
    # credit_notes = models.ForeignKey(
    #     CompanyDocument, models.DO_NOTHING,
    #     null=False, blank=False,
    #     help_text="Credit Notes/Discounts/Rebates Register",
    #     related_name="credit_notes"
    # )

    def __unicode__(self):
        return f"{self.company}'s Commercial Information"

