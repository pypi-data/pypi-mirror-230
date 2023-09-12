import django
from django import forms
from django.forms import widgets


if django.VERSION < (3, 2):
    from django.utils.translation import ugettext_lazy as _
else:
    from django.utils.translation import gettext_lazy as _

from .base import QuestionTypeBase


class SliderInput(widgets.Input):
    input_type = "range"


class RangeSlider(QuestionTypeBase):
    class Meta:
        name = "range_slider"
        verbose_name = _("Range (slider)")
        widget_class = SliderInput

    class OptionsForm(forms.Form):
        min = forms.IntegerField(required=True)
        max = forms.IntegerField(required=True)
        step = forms.IntegerField(required=True)

    def clean_question_options(self, question_options):
        """
        expected question_options format:
        {
            min: 1,
            max: 10,
            step: 1
        }
        """

        if "min" not in question_options:
            raise forms.ValidationError('key "min" required')
        try:
            question_options["min"] = int(question_options["min"])
        except ValueError:
            raise forms.ValidationError('value for "min" is not an integer')

        if "max" not in question_options:
            raise forms.ValidationError('key "max" required')
        try:
            question_options["max"] = int(question_options["max"])
        except ValueError:
            raise forms.ValidationError('value for "max" is not an integer')

        if question_options["min"] >= question_options["max"]:
            raise forms.ValidationError('value for "min" greater or equal to "max"')

        if "step" not in question_options:
            raise forms.ValidationError('key "step" required')
        if question_options.get("step"):
            try:
                question_options["step"] = int(question_options["step"])
            except ValueError:
                raise forms.ValidationError('value for "step" is not an integer')

        if question_options["step"] > question_options["max"]:
            raise forms.ValidationError('value for "step" greater than "max"')

        if question_options.get("initial"):
            try:
                question_options["initial"] = int(question_options["initial"])
            except ValueError:
                raise forms.ValidationError('value for "initial" is not an integer')

        return question_options

    def initial_field_value(self, result_set):
        initial = super().initial_field_value(result_set)
        return initial or self.question.question_options.get("initial")

    def formfield_widget_attrs(self):
        attrs = {
            "min": self.question.question_options.get("min"),
            "max": self.question.question_options.get("max"),
            "step": self.question.question_options.get("step", 1),
        }
        attrs.update(super().formfield_widget_attrs())
        return attrs

    def formfield(self, result_set):
        min_value = self.question.question_options.get("min")
        max_value = self.question.question_options.get("max")

        return forms.IntegerField(
            widget=self.formfield_widget(),
            min_value=min_value,
            max_value=max_value,
            required=self.question.required,
            label=self.question.question_text,
        )
