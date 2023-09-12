import django
from django import forms
from django.forms import widgets


if django.VERSION < (3, 2):
    from django.utils.translation import ugettext_lazy as _
else:
    from django.utils.translation import gettext_lazy as _

from .base import QuestionTypeBase


class MultipleTextWidget(widgets.MultiWidget):
    def decompress(self, value):
        return value or []


class MultipleTextField(forms.MultiValueField):
    # custom property indicating field needs to be recreated depending on POST data
    dynamic_count = True

    def __init__(self, fields, *args, **kwargs):
        self._question_type = kwargs.pop("question_type", None)
        super().__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        # drop empty entries
        return [v for v in data_list if v]

    def clean(self, value):
        compressed_value = super().clean(value)
        question = self._question_type.question
        if len(compressed_value) < question.question_options.get("min", int(question.required)):
            raise forms.ValidationError(self.error_messages["required"], code="required")
        return compressed_value

    def get_multi_field_count(self, post_data, field_id):
        count = 0
        subfield_prefix = "{}_".format(field_id)
        for subfield_id, field in post_data.items():
            if subfield_id.startswith(subfield_prefix):
                count += 1
        return count


class MultipleText(QuestionTypeBase):
    class Meta:
        name = "multiple_text"
        verbose_name = _("Multiple (Text)")
        multiple = True
        widget_class = MultipleTextWidget

    class OptionsForm(forms.Form):
        min = forms.IntegerField(required=False)
        min_length = forms.IntegerField(required=False)
        max_length = forms.IntegerField(required=False)

    def clean_question_options(self, question_options):
        if "min" in question_options:
            try:
                question_options["min"] = int(question_options["min"])
            except ValueError:
                raise forms.ValidationError('value for "min" is not an integer')
        if "min_length" in question_options:
            try:
                question_options["min_length"] = int(question_options["min_length"])
            except ValueError:
                raise forms.ValidationError('value for "min_length" is not an integer')
        if "max_length" in question_options:
            try:
                question_options["max_length"] = int(question_options["max_length"])
            except ValueError:
                raise forms.ValidationError('value for "max_length" is not an integer')

        return question_options

    def formfield_widget_attrs(self):
        attrs = dict()
        if self.question.question_options.get("min_length"):
            attrs.update({"minlength": self.question.question_options.get("min_length")})
        if self.question.question_options.get("max_length"):
            attrs.update({"maxlength": self.question.question_options.get("max_length")})
        attrs.update(super().formfield_widget_attrs())
        return attrs

    def formfield(self, result_set, min_fields: int = 1):
        fields = list()
        field_widgets = list()

        min_required = self.question.question_options.get("min", int(self.question.required))

        try:
            prev_answers = result_set.answers.filter(question=self.question).count()
        except ValueError:
            prev_answers = 0

        num_fields = max(prev_answers, min_required, min_fields)

        for field_num in range(0, num_fields):
            # validate required fields in MultipleTextField.clean()
            field = forms.CharField(
                required=False,
                min_length=self.question.question_options.get("min_length"),
                max_length=self.question.question_options.get("max_length"),
            )
            fields.append(field)
            # setup widget
            attrs = self.formfield_widget_attrs()
            # workaround to set required via js (required will be ignored by django if require_all_fields is True)
            if field_num == 0 and self.question.required:
                attrs.update({"data-required": True})
            field_widgets.append(widgets.TextInput(attrs=attrs))

        return MultipleTextField(
            fields=fields,
            widget=self.formfield_widget(widgets=field_widgets),
            required=False,
            require_all_fields=self.question.required,
            label=self.question.question_text,
            question_type=self,
        )
