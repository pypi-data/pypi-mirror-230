from collections import OrderedDict

from django.db import models, transaction
from django.utils.text import Truncator

from ordered_model.models import OrderedModel

from ..fields import QuestionTypeField
from ..forms import QuestionnaireFormBase
from ..question_types import QuestionTypeRegistry


try:
    # there is no difference in the (postgres) schema, so we can easily swap between the two
    from django.db.models import JSONField
except ImportError:
    from django.contrib.postgres.fields.jsonb import JSONField


def builtin_question_types():
    for question_type in sorted(
        QuestionTypeRegistry.get_question_types().values(),
        key=lambda q: q.meta.verbose_name,
    ):
        yield (question_type.meta.name, question_type.meta.verbose_name)


class QuestionnaireManager(models.Manager):
    def with_questions(self):
        return self.get_queryset().prefetch_related("questions")


class Questionnaire(models.Model):
    title = models.CharField(max_length=200)

    objects = QuestionnaireManager()

    def build_form_class(self, result_set):
        """Create form class for the questionnaire.

        :param result_set: result set used to save results and build initial form values
        :type result_set: questionnaire_core.models.QuestionnaireResult
        :return: form class for the questionnaire
        :rtype: QuestionnaireForm
        """
        question_form_dict = OrderedDict()

        # add question fields
        for question in self.questions.all():
            question_form_id = "q{}".format(question.pk)
            question_form_dict[question_form_id] = question.question_type_obj.formfield(result_set)

        # bind questionnaire & result_set to form
        question_form_dict["current_questionnaire"] = self
        question_form_dict["current_result_set"] = result_set

        form = type("QuestionnaireForm", (QuestionnaireFormBase,), question_form_dict)

        return form

    def __str__(self):
        return self.title

    def copy(self, title):
        questions = list(self.questions.all())

        with transaction.atomic():
            questionnaire_copy = Questionnaire.objects.create(
                title=title,
            )
            for question in questions:
                question.pk = None
                question.questionnaire = questionnaire_copy
                question.save()

        return questionnaire_copy


class Question(OrderedModel):
    questionnaire = models.ForeignKey(Questionnaire, related_name="questions", on_delete=models.CASCADE)
    question_text = models.CharField(max_length=5000)
    question_type = QuestionTypeField(max_length=32, choices=builtin_question_types())
    question_options = JSONField(blank=True, default=dict)
    required = models.BooleanField(default=True)

    order_with_respect_to = "questionnaire"

    class Meta(OrderedModel.Meta):
        pass

    def question_type_class(self):
        if self.question_type:
            return QuestionTypeRegistry.get_question_type(self.question_type)
        raise ValueError("question_type not set")

    @property
    def question_type_obj(self):
        return self.question_type_class()(question=self)

    def __str__(self):
        return Truncator(self.question_text).chars(20)
