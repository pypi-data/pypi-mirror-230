import os

from django.db import models

from .base import BaseModelAbstract


def upload_to(instance, filename):
    f, ext = os.path.splitext(filename)
    return f'feedbacks/{instance.id}-image1{ext}'


def upload_to2(instance, filename):
    f, ext = os.path.splitext(filename)
    return f'feedbacks/{instance.id}-image2{ext}'


class Feedback(BaseModelAbstract):
    type = models.CharField(max_length=50)
    feature = models.CharField(max_length=50)
    description = models.TextField()
    rating = models.IntegerField(default=0)
    image1 = models.ImageField(upload_to=upload_to, null=True, blank=True)
    image2 = models.ImageField(upload_to=upload_to2, null=True, blank=True)

    def __str__(self):
        return self.description
