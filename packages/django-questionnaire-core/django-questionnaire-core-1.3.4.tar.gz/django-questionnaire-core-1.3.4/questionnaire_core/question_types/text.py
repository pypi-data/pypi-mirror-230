import django
from django import forms


if django.VERSION < (3, 2):
    from django.utils.translation import ugettext_lazy as _
else:
    from django.utils.translation import gettext_lazy as _

from .base import QuestionTypeBase


class TextBase(QuestionTypeBase):
    class Meta:
        abstract = True

    class OptionsForm(forms.Form):
        min_length = forms.IntegerField(required=False)
        max_length = forms.IntegerField(required=False)

    def clean_question_options(self, question_options):
        """
        expected question_options format:
        {
            min_length: 10,
            max_length: 100
        }
        """

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


class TextShort(TextBase):
    class Meta:
        name = "text_short"
        verbose_name = _("Text (Short)")
        widget_class = forms.TextInput

    def formfield(self, result_set):
        min_length = self.question.question_options.get("min_length")
        max_length = self.question.question_options.get("max_length")

        return forms.CharField(
            widget=self.formfield_widget(),
            label=self.question.question_text,
            required=self.question.required,
            min_length=min_length,
            max_length=max_length,
        )


class TextLong(TextBase):
    class Meta:
        name = "text_long"
        verbose_name = _("Text (Long)")
        widget_class = forms.Textarea

    def formfield(self, result_set):
        min_length = self.question.question_options.get("min_length")
        max_length = self.question.question_options.get("max_length")

        return forms.CharField(
            widget=self.formfield_widget(),
            label=self.question.question_text,
            required=self.question.required,
            min_length=min_length,
            max_length=max_length,
        )
