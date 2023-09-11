from django.db import models
from .base import BaseModelAbstract


class Media(BaseModelAbstract):
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    type = models.CharField(max_length=20)
    is_local = models.BooleanField(default=True)

    def __str__(self):
        return self.url


class Video(BaseModelAbstract):
    topic = models.ForeignKey('Topic', models.CASCADE, null=False, blank=False)
    media = models.OneToOneField('Media', models.CASCADE)
    duration = models.IntegerField(null=False, blank=False, editable=False)

    def __str__(self):
        return f'{self.topic} - {self.media.name}'
