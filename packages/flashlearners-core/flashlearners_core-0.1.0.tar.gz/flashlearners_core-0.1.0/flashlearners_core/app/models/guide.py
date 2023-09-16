from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

from flashlearners_core import constants
from .base import BaseModelAbstract


class Guide(BaseModelAbstract):
    type = models.CharField(max_length=1, choices=constants.GUIDE_TYPES)
    title = models.CharField(max_length=100, null=False, blank=False)
    body = CKEditor5Field(null=False, blank=False)

    def __str__(self):
        return self.title


class Novel(BaseModelAbstract):
    # type = models.CharField(max_length=1, choices=constants.GUIDE_TYPES)
    title = models.CharField(max_length=100, null=False, blank=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class NovelChapter(BaseModelAbstract):
    novel = models.ForeignKey('Novel', models.CASCADE, null=False, blank=False)
    title = models.CharField(max_length=100, null=False, blank=False)
    body = CKEditor5Field(null=False, blank=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
