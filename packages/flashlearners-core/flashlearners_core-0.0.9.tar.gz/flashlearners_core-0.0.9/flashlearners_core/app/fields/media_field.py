import shutil

from django.core.files.storage import get_storage_class, default_storage
from django.db import models
from django.db.models.fields.files import FileDescriptor


class MediaFieldDescriptor(FileDescriptor):
    pass


class MediaField(models.FileField):
    descriptor_class = MediaFieldDescriptor

    def __init__(self, verbose_name=None, name=None, storage=None,
                 upload_to="", **kwargs):
        total, used, free = shutil.disk_usage('/')
        limit = 15  # 15gb
        free_gb = free / (10**9)
        print("MediaField", {"free_gb": free_gb, "storage": storage})
        if not free_gb <= limit:
            storage = get_storage_class(
                'django.core.files.storage.FileSystemStorage'
            )
            self.local = True
        else:
            self.local = False
            storage = None
        kwargs.setdefault('max_length', 255)
        super().__init__(verbose_name=verbose_name, name=name,
                         upload_to=upload_to, storage=storage, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if kwargs.get("max_length") == 255:
            del kwargs["max_length"]
        kwargs["upload_to"] = self.upload_to
        storage = getattr(self, "_storage_callable", self.storage)
        if storage is not default_storage:
            kwargs["storage"] = storage
        return name, path, args, kwargs

    def to_python(self, value):
        return super().to_python(value)

    def _set_storage(self, name):
        st = name.split('|')[-1]
        if st == 'local':
            self.storage = get_storage_class(
                'django.core.files.storage.FileSystemStorage'
            )()
        else:
            self.storage = default_storage

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        self._set_storage(value)
        return value.split('|')[0]

    def value_to_string(self, obj):
        out = super().value_to_string(obj)
        self._set_storage(out)
        return out

    def get_prep_value(self, value):
        out = super().get_prep_value(value)
        return f"{out}|{'local' if self.local else 's3'}"
