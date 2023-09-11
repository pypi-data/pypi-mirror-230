import datetime

from django.db import models
from django.utils import timezone

from flashlearners_core import constants
from .base import BaseModelAbstract


class Subscription(BaseModelAbstract):
    plan = models.CharField(max_length=1, choices=constants.PLAN_MODES)
    expiry = models.DateTimeField(null=True, blank=True)
    expired = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.expiry:
            self.expiry = timezone.now() + datetime.timedelta(days=365)
        super().save(*args, **kwargs)
