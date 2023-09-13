from django.core.validators import FileExtensionValidator
from django.db import models

from . import settings


class QuestionTypeField(models.CharField):
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # don't serialize kwargs set at runtime
        kwargs.pop("choices", None)
        return name, path, args, kwargs


class DynamicStorageFileField(models.FileField):
    def __init__(self, verbose_name=None, name=None, upload_to="", storage=None, **kwargs):
        if not storage and settings.upload_storage:
            storage = settings.upload_storage
        if not upload_to and settings.upload_to_handler:
            upload_to = settings.upload_to_handler
        if settings.upload_allowed_file_extensions:
            if not kwargs.get("validators"):
                kwargs["validators"] = list()
            kwargs["validators"].append(
                FileExtensionValidator(allowed_extensions=settings.upload_allowed_file_extensions)
            )
        super().__init__(verbose_name, name, upload_to, storage, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # don't serialize kwargs set at runtime by project settings
        kwargs.pop("storage", None)
        kwargs.pop("upload_to", None)
        kwargs.pop("validators", None)
        return name, path, args, kwargs
