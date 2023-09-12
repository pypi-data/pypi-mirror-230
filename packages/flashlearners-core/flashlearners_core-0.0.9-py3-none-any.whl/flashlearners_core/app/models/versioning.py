from django.db import models


class Versioning(models.Model):
    subject = models.IntegerField(default=1)
    topic = models.IntegerField(default=1)
    question = models.IntegerField(default=1)
    option = models.IntegerField(default=1)
    flashcard = models.IntegerField(default=1)
    novel = models.IntegerField(default=1)
    novel_chapter = models.IntegerField(default=1)
