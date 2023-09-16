import os

from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

from flashlearners_core import constants
from .base import BaseModelAbstract


def upload_to(instance, filename):
    f, ext = os.path.splitext(filename)
    return f'questions/{instance.id}{ext}'


def upload_to2(instance, filename):
    f, ext = os.path.splitext(filename)
    return f'options/{instance.id}{ext}'


class Session(BaseModelAbstract):
    name = models.CharField(max_length=30, unique=True)
    year = models.IntegerField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-year', )


class Question(BaseModelAbstract):
    type = models.CharField(max_length=1, choices=constants.QUESTION_TYPES)
    category = models.CharField(max_length=1, choices=constants.QUIZ_TYPES)
    session = models.ForeignKey('Session', models.CASCADE,
                                null=True, blank=True)
    subject = models.ForeignKey('Subject', models.CASCADE)
    topic = models.ForeignKey('Topic', models.SET_NULL, null=True)
    text = CKEditor5Field(null=True, blank=True)
    explanation = CKEditor5Field(null=True, blank=True)
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
    text = CKEditor5Field(null=True, blank=True)
    correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question} - {self.text}"

    @property
    def title(self):
        x = (self.text or 'Image only')
        if len(x) > 30:
            return f"{x[:30]}..."
        return x