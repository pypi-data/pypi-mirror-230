import os

from django.db import models

from flashlearners_core import constants
from .base import BaseModelAbstract
from ..fields.media_field import MediaField


def upload_to(instance, filename):
    f, ext = os.path.splitext(filename)
    return f'notifications/{instance.id}{ext}'


class Notification(BaseModelAbstract):
    icon = models.ImageField(upload_to=upload_to)
    title = models.CharField(max_length=100)
    body = models.TextField()

    def __str__(self):
        return self.title


class NotificationToken(BaseModelAbstract):
    token = models.TextField()
    type = models.CharField(max_length=1, choices=constants.PUSH_TOKEN_TYPES,
                            default=constants.ONE_SIGNAL_PUSH_TOKEN_TYPE)
