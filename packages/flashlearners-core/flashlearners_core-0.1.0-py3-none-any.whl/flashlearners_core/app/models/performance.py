from django.db import models
from flashlearners_core import constants
from .base import BaseModelAbstract


class Performance(BaseModelAbstract):
    type = models.CharField(max_length=1, choices=constants.QUIZ_TYPES)
    duration = models.IntegerField(default=0)
    number_of_questions = models.IntegerField(default=0)


class PerformanceItem(BaseModelAbstract):
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
