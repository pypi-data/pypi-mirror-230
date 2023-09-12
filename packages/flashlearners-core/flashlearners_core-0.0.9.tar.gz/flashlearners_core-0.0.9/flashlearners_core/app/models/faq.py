from django.db import models

from flashlearners_core import constants
from .base import BaseModelAbstract


class Faq(BaseModelAbstract):
    question = models.CharField(max_length=255)
    type = models.CharField(max_length=1, choices=constants.FAQ_TYPES)
    answer = models.TextField(null=False, blank=False)

    def __str__(self):
        return self.question
