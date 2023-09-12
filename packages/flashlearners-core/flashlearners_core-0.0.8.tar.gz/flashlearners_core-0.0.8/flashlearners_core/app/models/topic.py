from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

from .base import BaseModelAbstract


class Topic(BaseModelAbstract):
    subject = models.ForeignKey('Subject', models.CASCADE)
    parent = models.ForeignKey("self", models.CASCADE, null=True, blank=True)
    name = models.CharField(unique=True, max_length=100)
    notes = CKEditor5Field(null=True, blank=True)
    allow_free = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        if self.parent:
            return f"{self.parent} - {self.name}"
        return f"{self.subject} - {self.name}"
    
