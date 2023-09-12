from django.db import models

from .base import BaseModelAbstract


class Subject(BaseModelAbstract):
    name = models.CharField(unique=True, max_length=100)
    image = models.ForeignKey('Media', models.SET_NULL, null=True, blank=True)
    requires_calculator = models.BooleanField(default=False)
    allow_free = models.BooleanField(default=False)
    current_affair = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

