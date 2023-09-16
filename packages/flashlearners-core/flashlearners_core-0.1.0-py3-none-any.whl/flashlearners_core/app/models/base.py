import uuid
from django.db import models


class BaseModelAbstract(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('User', null=True, editable=False,
                                   on_delete=models.SET_NULL,
                                   blank=True)
    
    class Meta:
        abstract = True
        ordering = ('-created_at', )

    def __unicode__(self):
        return self.__str__()
