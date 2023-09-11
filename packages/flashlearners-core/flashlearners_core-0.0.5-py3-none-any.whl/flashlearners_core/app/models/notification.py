from django.db import models

from flashlearners_core import constants
from .base import BaseModelAbstract


class Notification(BaseModelAbstract):
    icon = models.ForeignKey('Media', models.CASCADE)
    title = models.CharField(max_length=100)
    body = models.TextField()

    def __str__(self):
        return self.title


class NotificationToken(BaseModelAbstract):
    token = models.TextField()
    type = models.CharField(max_length=1, choices=constants.PUSH_TOKEN_TYPES,
                            default=constants.ONE_SIGNAL_PUSH_TOKEN_TYPE)
