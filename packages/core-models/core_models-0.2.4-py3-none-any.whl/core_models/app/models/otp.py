from datetime import timedelta

from django.db import models
from django.utils import timezone

from core_models.app import notification_manager
from core_models.utils import random_numbers


class Otp(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        Otp.objects.filter(email=self.email).delete()
        self.code = random_numbers(6)
        self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)
        notification_manager.send_mail(
            subject='[Action Required] Liquify Verification',
            template_dir="verification-code",
            to=[self.email],
            context_dict={
                "expiry": self.expires_at,
                "code": self.code
            }
        )

    @staticmethod
    def verify(email: str, code: str) -> bool:
        try:
            otp = Otp.objects.get(
                email=email, code=code,
                expires_at__gt=timezone.now()
            )
            otp.delete()
            return True
        except:
            return False
