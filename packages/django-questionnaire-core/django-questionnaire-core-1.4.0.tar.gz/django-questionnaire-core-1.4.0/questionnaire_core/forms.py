from django import forms
from django.db import transaction


class QuestionnaireFormBase(forms.Form):
    """Base form for questionnaires.

    Fields are added dynamically by `Questionnaire.build_form_class()`.
    """

    def __init__(self, *args, **kwargs):
        # Property which can optionally be passed into form which sets all fields to disabled.
        readonly_form = kwargs.pop("is_readonly", False)

        super().__init__(*args, **kwargs)

        if readonly_form:
            for field_id, field in self.fields.items():
                field.disabled = True

        if self.data:
            for field_id, field in self.fields.items():
                if hasattr(field, "dynamic_count"):
                    field_num = field.get_multi_field_count(self.data, field_id)
                    if field_num > 0:
                        self.fields[field_id] = field._question_type.formfield(
                            self.current_result_set,
                            min_fields=field_num,
                        )

    def clean(self):
        # per field (question/answer) validation
        for question in self.current_questionnaire.questions.all():
            field_id = "q{}".format(question.pk)
            answer_data = self.cleaned_data.get(field_id)
            try:
                self.cleaned_data[field_id] = question.question_type_obj.clean_answer_data(answer_data)
            except forms.ValidationError as e:
                self.add_error(field_id, e)

        return super().clean()

    @transaction.atomic
    def save(self, result_meta=None):
        result_set = self.current_result_set
        if result_set.pk:
            # on update remove previous answers (except uploaded files)
            result_set.answers.exclude(question__question_type__istartswith="file").delete()
        else:
            if result_meta is not None:
                result_set.result_meta = result_meta
            result_set.save()

        for question in self.current_questionnaire.questions.all():
            answer_data = self.cleaned_data.get("q{}".format(question.pk))
            question.question_type_obj.save(result_set, answer_data)

        return result_set
