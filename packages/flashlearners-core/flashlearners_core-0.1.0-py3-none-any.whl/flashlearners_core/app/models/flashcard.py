from django.db import models


from .base import BaseModelAbstract


class FlashCard(BaseModelAbstract):
    topic = models.ForeignKey('Topic', models.CASCADE, null=False, blank=False)
    question = models.CharField(max_length=255)
    answer = models.TextField(null=False, blank=False)

    def __str__(self):
        return self.question
