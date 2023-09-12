import django
from django import forms


if django.VERSION < (3, 2):
    from django.utils.translation import ugettext_lazy as _
else:
    from django.utils.translation import gettext_lazy as _

from .base import QuestionTypeBase


class Boolean(QuestionTypeBase):
    class Meta:
        name = "boolean"
        verbose_name = _("Boolean (Checkbox)")
        widget_class = forms.CheckboxInput

    def formfield(self, result_set):
        return forms.BooleanField(
            widget=self.formfield_widget(),
            label=self.question.question_text,
            required=self.question.required,
        )


class BooleanYesNo(QuestionTypeBase):
    class Meta:
        name = "boolean_yesno"
        verbose_name = _("Boolean (Yes/No)")
        widget_class = forms.RadioSelect

    def formfield(self, result_set):
        return forms.TypedChoiceField(
            widget=self.formfield_widget(),
            label=self.question.question_text,
            required=self.question.required,
            coerce=lambda x: x == "True",
            choices=((True, _("Yes")), (False, _("No"))),
        )
