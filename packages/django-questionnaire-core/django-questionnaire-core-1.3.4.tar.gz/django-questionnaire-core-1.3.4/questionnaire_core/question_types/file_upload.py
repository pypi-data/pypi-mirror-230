import os
from contextlib import suppress

import django
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.forms import widgets


if django.VERSION < (3, 2):
    from django.utils.translation import ugettext_lazy as _
else:
    from django.utils.translation import gettext_lazy as _

from .base import QuestionTypeBase


class CustomFileInput(widgets.ClearableFileInput):
    input_type = "file"

    def format_value(self, value):
        """
        Return the file object if it has a defined url attribute.
        """
        if self.is_initial(value):
            value.filename = os.path.basename(value.file.name)  # add filename attribute for usage in widget
            return value


class FileUpload(QuestionTypeBase):
    class Meta:
        name = "file_upload"
        verbose_name = _("File upload")
        widget_class = CustomFileInput

    def formfield(self, result_set):
        required: bool = self.question.required

        # disable required flag if field was originally required and file has already been uploaded
        if result_set.pk and self.question.required:
            with suppress(ObjectDoesNotExist):
                result_set.answers.get(question=self.question)
                required = False

        return forms.FileField(
            widget=self.formfield_widget(),
            label=self.question.question_text,
            required=required,
        )

    def initial_field_value(self, result_set):
        with suppress(ObjectDoesNotExist, ValueError):
            answer = result_set.answers.get(question=self.question)
            return answer.file_upload.file

    def save(self, result_set, file_upload):
        from ..models import AnswerFile, QuestionAnswer

        if file_upload is None:
            return

        try:
            answer = result_set.answers.get(question=self.question)
        except (ObjectDoesNotExist, ValueError):
            answer = None

        with transaction.atomic():
            # remove uploaded file ("clear" checkbox checked)
            if file_upload is False and answer is not None:
                answer.file_upload.delete()
                answer.delete()
                return

            # save some metadata in answer_data
            file_upload_name = os.path.basename(file_upload.name)
            answer_data = {
                "name": file_upload_name,
                "size": file_upload.size,
            }
            if not answer:
                answer = QuestionAnswer.objects.create(
                    result_set=result_set,
                    question=self.question,
                    answer_data=answer_data,
                )
            else:
                answer.answer_data = answer_data
                answer.save()

            if not hasattr(answer, "file_upload"):
                AnswerFile.objects.create(answer=answer, file=file_upload)
            else:
                # delete previously uploaded file from storage & update file_upload field
                answer.file_upload.file.delete(save=False)
                answer.file_upload.file.save(file_upload_name, file_upload, save=True)
