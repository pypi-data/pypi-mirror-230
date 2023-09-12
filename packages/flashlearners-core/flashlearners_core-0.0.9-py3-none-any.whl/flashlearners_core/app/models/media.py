import os

from django.db import models
from .base import BaseModelAbstract
from ..fields.media_field import MediaField


def upload_to(instance, filename):
    f, ext = os.path.splitext(filename)
    return f'videos/{instance.id}{ext}'


class Video(BaseModelAbstract):
    topic = models.ForeignKey('Topic', models.CASCADE, null=False, blank=False)
    title = models.CharField(max_length=255)
    file = MediaField(upload_to=upload_to)
    duration = models.IntegerField(null=False, blank=False, editable=False)

    def __str__(self):
        return f'{self.topic} - {self.title}'
