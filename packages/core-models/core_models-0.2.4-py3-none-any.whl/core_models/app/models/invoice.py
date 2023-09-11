from _decimal import Decimal

from django.db import models
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field
from model_utils import FieldTracker

from core_models import constants
from core_models.app.models import User, Currency
from .base import BaseModelAbstract
from .. import NotificationManager


class Invoice(BaseModelAbstract, models.Model):
    seller = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, related_name='sent_invoices')
    buyer = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, related_name='received_invoices')
    financier = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, related_name='funded_invoices')
    currency = models.ForeignKey(Currency, models.SET_NULL, null=True, blank=True)
    reference = models.CharField(max_length=20, null=True, blank=True, editable=False)
    invoice_number = models.CharField(max_length=50, null=False, blank=False)
    subtotal = models.DecimalField(decimal_places=2, max_digits=30, null=False, blank=False)
    total = models.DecimalField(decimal_places=2, max_digits=30, null=False, blank=False)
    discount = models.DecimalField(decimal_places=2, max_digits=30, default=0)
    tax = models.DecimalField(decimal_places=2, max_digits=30, default=0)
    invoice_date = models.DateField(null=False, blank=False)
    due_date = models.DateField(null=False, blank=False)
    financed_on = models.DateTimeField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=constants.INVOICE_STATUSES,
                              default=constants.NEW_INVOICE_STATUS)
    recurring = models.BooleanField(default=False)
    seller_risk_percentage = models.FloatField(default=0)
    buyer_risk_percentage = models.FloatField(default=0)
    base_rate = models.FloatField(default=0)
    interest_rate = models.FloatField(default=0, editable=False)
    interest = models.DecimalField(decimal_places=2, max_digits=30, default=0)
    liquify_fee = models.DecimalField(decimal_places=2, max_digits=30, default=0)
    buyer_amount = models.DecimalField(decimal_places=2, max_digits=30, default=0)
    seller_amount = models.DecimalField(decimal_places=2, max_digits=30, default=0)
    financier_amount = models.DecimalField(decimal_places=2, max_digits=30, default=0)
    metadata = models.JSONField(null=True, blank=True)
    rpa = CKEditor5Field(editable=False, null=True, blank=True)

    tracker = FieldTracker(fields=['status'])

    def save(self, keep_deleted=False, **kwargs):
        if not self.reference:
            now = timezone.now()
            self.reference = f"LQIN{now.strftime('%Y%m%d%H%M%S')}"
        if self.base_rate and self.seller_risk_percentage and self.buyer_risk_percentage:
            self.interest_rate = sum([self.base_rate, self.seller_risk_percentage, self.buyer_risk_percentage])
            self.interest = round(self.total * round(Decimal(
                self.interest_rate)/100, 2), 2)
            self.buyer_amount = self.total
            self.financier_amount = self.total - self.interest
            self.seller_amount = self.financier_amount - self.liquify_fee
        status_changed = self.tracker.has_changed('status') or not self.id
        super(Invoice, self).save(keep_deleted, **kwargs)
        if status_changed:
            NotificationManager.save_invoice_notification(self)

    def __unicode__(self):
        return self.reference


class InvoiceItem(BaseModelAbstract, models.Model):
    invoice = models.ForeignKey(Invoice, models.CASCADE, related_name="items")
    title = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    price = models.DecimalField(decimal_places=2, max_digits=20, help_text='Unit Price')
    total = models.DecimalField(decimal_places=2, max_digits=20)
    quantity = models.DecimalField(default=1, decimal_places=2, max_digits=10)

    def __unicode__(self):
        return f"{self.invoice} item"

    def calc_total(self):
        return self.price * self.quantity

    def save(self, keep_deleted=False, **kwargs):
        self.total = self.calc_total()
        super(InvoiceItem, self).save(keep_deleted, **kwargs)
