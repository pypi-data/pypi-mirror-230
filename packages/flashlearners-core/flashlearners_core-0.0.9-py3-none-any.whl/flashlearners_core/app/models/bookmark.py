from django.db import models

from flashlearners_core import constants
from .base import BaseModelAbstract


class Bookmark(BaseModelAbstract):
    created_by = models.ForeignKey('User', models.CASCADE, related_name='bookmarks')
    object_id = models.UUIDField()
    object_type = models.CharField(max_length=1, choices=constants.BOOKMARK_TYPES)

    def __str__(self):
        return f"{self.object_type} Bookmark by {self.created_by}"
