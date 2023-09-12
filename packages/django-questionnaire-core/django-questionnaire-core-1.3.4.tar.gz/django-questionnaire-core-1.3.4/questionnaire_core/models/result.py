from collections import OrderedDict

from django.db import models

from ordered_model.models import OrderedModel

from ..fields import DynamicStorageFileField
from .questionnaire import Question, Questionnaire


try:
    # there is no difference in the (postgres) schema, so we can easily swap between the two
    from django.db.models import JSONField
except ImportError:
    from django.contrib.postgres.fields.jsonb import JSONField


class QuestionnaireResultManager(models.Manager):
    def with_answers(self):
        return self.get_queryset().prefetch_related("answers")


class QuestionnaireResult(models.Model):
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    result_meta = JSONField(
        default=dict,
        help_text="Optional JSON field for application specific meta data",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = QuestionnaireResultManager()

    def initial_form_data(self):
        initial_data = OrderedDict()

        initial_data["result_set"] = self.pk
        for question in self.questionnaire.questions.all():
            form_field_id = "q{}".format(question.pk)
            form_field_value = question.question_type_obj.initial_field_value(self)
            if form_field_value is not None:
                initial_data[form_field_id] = form_field_value

        return initial_data

    def __str__(self):
        return "{} ({})".format(self.questionnaire, self.created_at)


class QuestionAnswer(OrderedModel):
    result_set = models.ForeignKey(QuestionnaireResult, related_name="answers", on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name="answers", on_delete=models.CASCADE)
    answer_data = JSONField(null=True, db_index=True)

    order_with_respect_to = "result_set"

    class Meta(OrderedModel.Meta):
        pass

    def __str__(self):
        return "{}: {}".format(self.question, self.answer_data)


class AnswerFile(OrderedModel):
    answer = models.OneToOneField(QuestionAnswer, related_name="file_upload", on_delete=models.CASCADE)
    file = DynamicStorageFileField()

    order_with_respect_to = "answer"

    class Meta(OrderedModel.Meta):
        pass
