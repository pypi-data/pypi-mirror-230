import time
from django.db import models
from .base import BaseModelAbstract


class Payment(BaseModelAbstract):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    mode = models.CharField(max_length=30)
    depositor = models.CharField(null=True, blank=True, max_length=255)
    reference = models.CharField(max_length=255)
    status = models.CharField(max_length=30, default='pending')

    def save(self, keep_deleted=False, **kwargs):
        if not self.reference:
            self.reference = f"{time.time_ns()}"
        super(Payment, self).save(keep_deleted, **kwargs)

    def __str__(self):
        return f"{self.created_by} - {self.amount} - {self.status}"
