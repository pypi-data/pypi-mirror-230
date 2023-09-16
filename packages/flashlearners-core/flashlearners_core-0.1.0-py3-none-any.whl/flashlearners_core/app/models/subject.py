import os

from django.db import models

from .base import BaseModelAbstract
from ..fields.media_field import MediaField


def upload_to(instance, filename):
    f, ext = os.path.splitext(filename)
    return f'subjects/{instance.id}{ext}'


class Subject(BaseModelAbstract):
    name = models.CharField(unique=True, max_length=100)
    image = models.ImageField(upload_to=upload_to)
    requires_calculator = models.BooleanField(default=False)
    allow_free = models.BooleanField(default=False)
    current_affair = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

