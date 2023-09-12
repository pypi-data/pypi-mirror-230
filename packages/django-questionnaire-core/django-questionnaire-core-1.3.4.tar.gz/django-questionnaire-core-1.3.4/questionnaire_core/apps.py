from django.apps import AppConfig


class QuestionnaireCoreConfig(AppConfig):
    name = "questionnaire_core"

    def ready(self):
        # validate settings on startup
        from . import settings

        # update question type choices on `Question` model
        from .models import Question

        question_type_choices = [(qt.meta.name, qt.meta.verbose_name) for qt in settings.active_question_types]
        question_type_field = Question._meta.get_field("question_type")
        question_type_field.choices = question_type_choices
