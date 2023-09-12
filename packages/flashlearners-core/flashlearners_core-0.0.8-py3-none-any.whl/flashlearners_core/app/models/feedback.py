from django.db import models

from .base import BaseModelAbstract


class Feedback(BaseModelAbstract):
    type = models.CharField(max_length=50)
    feature = models.CharField(max_length=50)
    description = models.TextField()
    rating = models.IntegerField(default=0)

    def __str__(self):
        return self.description
