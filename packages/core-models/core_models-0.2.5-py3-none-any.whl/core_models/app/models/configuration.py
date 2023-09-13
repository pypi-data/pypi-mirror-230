from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
# from django_quill.fields import QuillField

from core_models import constants
from core_models.app.models import User


class Configuration(models.Model):
    rpa = CKEditor5Field(
        help_text='Use {seller_first_name}, {seller_last_name}, '
                  '{seller_company_name}, {seller_address}, '
                  '{buyer_first_name}, {buyer_last_name}, '
                  '{buyer_company_name}, {buyer_address}, '
                  '{financier_first_name}, {financier_last_name}, '
                  '{financier_company_name}, {financier_address}, '
                  '{current_day}, {current_month}, {current_year}, '
                  '{discount_percent}, {discount_amount}, {invoice_amount}, ',
        null=True, blank=True
    )
    liquify_fee = models.DecimalField(max_digits=15, decimal_places=2)
    liquify_fee_type = models.CharField(max_length=1, choices=constants.LIQUIFY_FEE_TYPES)
    last_updated_by = models.ForeignKey(User, models.SET_NULL, null=True, blank=True)
    last_updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Configuration #{self.pk}"
