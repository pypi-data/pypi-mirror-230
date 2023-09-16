import os

from django.db import models
from .base import BaseModelAbstract


def upload_to(instance, filename):
    f, ext = os.path.splitext(filename)
    return f'videos/{instance.id}{ext}'


class Video(BaseModelAbstract):
    topic = models.ForeignKey('Topic', models.CASCADE, null=False, blank=False)
    title = models.CharField(max_length=255)
    file = models.ImageField(upload_to=upload_to)
    duration = models.IntegerField(default=0, editable=False)

    def __str__(self):
        return f'{self.topic} - {self.title}'

    # def save(self, *args, **kwargs):
    #     if not bool(self.duration):
    #         self.duration = 1
    #     super().save(*args, **kwargs)
