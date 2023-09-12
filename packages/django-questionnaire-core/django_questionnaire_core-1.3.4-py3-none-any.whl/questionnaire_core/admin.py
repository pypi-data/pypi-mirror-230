import json

from django.contrib import admin
from django.forms import widgets

from ordered_model.admin import OrderedTabularInline

from .models import Question, QuestionAnswer, Questionnaire, QuestionnaireResult


try:
    # there is no difference in the (postgres) schema, so we can easily swap between the two
    from django.db.models import JSONField
except ImportError:
    from django.contrib.postgres.fields.jsonb import JSONField


try:
    from ordered_model.admin import OrderedInlineModelAdminMixin  # v3+
except ImportError:

    class OrderedInlineModelAdminMixin(object):
        def get_urls(self):
            urls = super().get_urls()
            for inline in self.inlines:
                if hasattr(inline, "get_urls"):
                    urls = inline.get_urls(self) + urls
            return urls


class PrettyJSONWidget(widgets.Textarea):
    def format_value(self, value):
        try:
            return json.dumps(json.loads(value), indent=2)  # reformat json
        except TypeError:
            return value


class QuestionnaireQuestionListModelInline(OrderedTabularInline):
    model = Question
    fields = (
        "question_type",
        "question_text",
        "question_options",
        "required",
        "order",
        "move_up_down_links",
    )
    readonly_fields = (
        "order",
        "move_up_down_links",
    )
    extra = 1
    ordering = ("order",)
    formfield_overrides = {
        JSONField: {"widget": PrettyJSONWidget},
    }


class QuestionnaireAnswerListModelInline(OrderedTabularInline):
    model = QuestionAnswer
    fields = (
        "question",
        "answer_data",
        "order",
        "move_up_down_links",
    )
    readonly_fields = (
        "order",
        "move_up_down_links",
    )
    extra = 0
    ordering = ("order",)


@admin.register(Questionnaire)
class QuestionnaireAdmin(OrderedInlineModelAdminMixin, admin.ModelAdmin):
    list_display = ("title",)
    inlines = (QuestionnaireQuestionListModelInline,)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question_text", "question_type", "questionnaire", "required")


@admin.register(QuestionnaireResult)
class QuestionnaireResultAdmin(OrderedInlineModelAdminMixin, admin.ModelAdmin):
    readonly_fields = ("created_at", "updated_at")
    inlines = (QuestionnaireAnswerListModelInline,)


@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(admin.ModelAdmin):
    pass
