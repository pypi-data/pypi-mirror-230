from django.db import models

from flashlearners_core import constants
from .base import BaseModelAbstract


class Question(BaseModelAbstract):
    type = models.CharField(max_length=1, choices=constants.QUESTION_TYPES)
    subject = models.ForeignKey('Subject', models.CASCADE)
    topic = models.ForeignKey('Topic', models.SET_NULL, null=True)
    text = models.TextField(null=True, blank=True)
    image = models.ForeignKey('Media', models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.subject} - {self.topic} - {self.title}"

    @property
    def title(self):
        x = (self.text or 'Image only')
        if len(x) > 30:
            return f"{x[:30]}..."
        return x


class Option(BaseModelAbstract):
    question = models.ForeignKey(Question, models.CASCADE,
                                 related_name='options')
    text = models.TextField(null=True, blank=True)
    image = models.ForeignKey('Media', models.CASCADE, null=True, blank=True)
    correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question} - {self.text}"

    @property
    def title(self):
        x = (self.text or 'Image only')
        if len(x) > 30:
            return f"{x[:30]}..."
        return x