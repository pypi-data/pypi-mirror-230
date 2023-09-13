import inspect
import string
from contextlib import suppress

from django import forms
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.template.engine import Engine
from django.template.exceptions import TemplateDoesNotExist


class QuestionTypeRegistry:
    """Registry for question type classes."""

    _registered_types = {}

    @classmethod
    def register(cls, question_type):
        name = question_type.meta.name
        cls._registered_types[name] = question_type

    @classmethod
    def unregister(cls, question_type):
        name = question_type.meta.name
        if name in cls._registered_types:
            del cls._registered_types[name]

    @classmethod
    def get_question_types(cls):
        return cls._registered_types

    @classmethod
    def get_question_type(cls, name: str):
        return cls._registered_types.get(name, None)


class Options:
    """Class to hold `meta` options of a question type class."""

    REQUIRED = ("name", "verbose_name")
    NAME_VALID_CHARS = string.ascii_lowercase + string.digits + "_"

    def __init__(self, cls, meta):
        for required_option in self.REQUIRED:
            if not meta.get(required_option, None):
                raise AttributeError('{}.Meta missing required field "{}"'.format(cls.__name__, required_option))

        if not set(self.NAME_VALID_CHARS).issuperset(set(meta.get("name"))):
            raise ValueError(
                "Invalid name for question type class {}: {} (valid chars: {})".format(
                    cls.__name__,
                    meta.get("name"),
                    self.NAME_VALID_CHARS,
                )
            )

        self.name = meta.get("name")
        self.verbose_name = meta.get("verbose_name")
        self.multiple = meta.get("multiple", False)
        self.widget_class = meta.get("widget_class", None)
        self._widget_template_name = meta.get("widget_template_name")
        self._widget_option_template_name = meta.get("widget_option_template_name")

    @property
    def widget_template_name(self):
        return self._widget_template_name or self.select_default_template("template_name")

    @property
    def widget_option_template_name(self):
        return self._widget_option_template_name or self.select_default_template("option_template_name")

    def select_default_template(self, template_key: str):
        """Select default template for the formfield widget.

        Returns the packaged template for the widget if available.
        """
        if template_key == "template_name":
            default_template = "questionnaire_core/widgets/{name}.html".format(name=self.name)
        elif template_key == "option_template_name":
            default_template = "questionnaire_core/widgets/{name}_option.html".format(name=self.name)
        else:
            return

        with suppress(TemplateDoesNotExist):
            template_engine = Engine.get_default()
            packaged_template = template_engine.get_template(default_template)
            return packaged_template.name


class QuestionTypeMeta(type):
    """Meta class for question type classes.

    Responsible for registering question type classes with QuestionTypeRegistry
    and setting up the `meta` attribute of question type classes.
    """

    def __new__(mcs, name, bases, attrs):
        super_new = super(QuestionTypeMeta, mcs).__new__

        # register only subclasses of QuestionTypeBase not QuestionTypeBase itself
        if name == "QuestionTypeBase":
            return super_new(mcs, name, bases, attrs)

        attr_meta = attrs.pop("Meta", None)

        # don't register abstract classes
        if getattr(attr_meta, "abstract", False):
            return super_new(mcs, name, bases, attrs)

        if not attr_meta or not inspect.isclass(attr_meta):
            raise AttributeError("{}.Meta attribute missing or not a class".format(name))

        new_class = super_new(mcs, name, bases, attrs)

        # create meta attribute (instance of Options) from new_class.Meta (similar to Model._meta)
        setattr(new_class, "meta", Options(new_class, attr_meta.__dict__))

        QuestionTypeRegistry.register(new_class)

        return new_class


class QuestionTypeBase(object, metaclass=QuestionTypeMeta):
    """Base class for question type classes"""

    class OptionsForm(forms.Form):
        pass

    def __init__(self, question):
        self.question = question

    def question_option_form(self, *args, **kwargs):  # arg0: request (optional)
        return self.OptionsForm

    @classmethod
    def question_option_form_fields(cls):
        return cls.OptionsForm.base_fields

    def clean_question_options(self, question_options):
        """Clean question options (`Question.question_options`).

        Override to implement any custom validations of the question options of the question type.

        :param question_options: django admin form field data
        :type question_options: dict
        :return: cleaned form field data
        :rtype: dict
        :raises: django.forms.ValidationError: Validation error
        """
        return question_options

    def clean_answer_data(self, data):
        """Clean answer data (`QuestionAnswer.answer_data`).

        :param data: data returned from the formfield
        :return: cleaned formfield data
        :raises: django.forms.ValidationError: Validation error
        """
        return data

    def formfield(self, result_set):
        """Form field for the question type.

        :param result_set: result set of the current form
        :type result_set: questionnaire_core.models.QuestionnaireResult
        :return: django form field for the question type
        :rtype: django.forms.Field
        """
        raise NotImplementedError

    def formfield_widget(self, **kwargs):
        """Setup and return the widget for the formfield."""
        widget_attrs = self.formfield_widget_attrs()
        if "attrs" in kwargs:
            widget_attrs.update(kwargs.get("attrs"))
        kwargs["attrs"] = widget_attrs
        widget = self.widget_class()(**kwargs)
        # set template attribute(s) of the widget
        for template_key in ("template_name", "option_template_name"):
            meta_template_key = "widget_{}".format(template_key)
            if getattr(self.question.question_type_obj.meta, meta_template_key) and hasattr(widget, template_key):
                setattr(
                    widget,
                    template_key,
                    getattr(self.question.question_type_obj.meta, meta_template_key),
                )
        return widget

    def widget_class(self):
        """Return the configured widget class for the formfield."""
        if not self.meta.widget_class:
            raise ValueError("{}.Meta.widget_class attribute is missing.".format(self.__class__.__name__))
        return self.meta.widget_class

    def formfield_widget_attrs(self):
        """Setup and return the attributes for the formfield widget (based on question options)."""
        attrs = dict()
        if "autocomplete" in self.question.question_options:
            attrs.update({"autocomplete": "on" if self.question.question_options.get("autocomplete") else "off"})
        return attrs

    def initial_field_value(self, result_set):
        """Return the initial formfield value based on the supplied result set."""
        if result_set.pk is None:
            return None
        elif self.question.question_type_obj.meta.multiple:
            return list(result_set.answers.filter(question=self.question).values_list("answer_data", flat=True))
        else:
            try:
                answer = result_set.answers.get(question=self.question)
                return answer.answer_data
            except ObjectDoesNotExist:
                return None
            except MultipleObjectsReturned:
                raise ValueError("Multiple answers found for QuestionType with multiple=False")

    def save(self, result_set, answer_data):
        from ..models import QuestionAnswer

        if self.meta.multiple:
            assert isinstance(answer_data, list)
            for answer_data_part in answer_data:
                QuestionAnswer.objects.create(
                    result_set=result_set,
                    question=self.question,
                    answer_data=answer_data_part,
                )
        else:
            QuestionAnswer.objects.create(
                result_set=result_set,
                question=self.question,
                answer_data=answer_data,
            )
