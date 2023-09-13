from django.views.generic import FormView


class QuestionnaireFormView(FormView):
    """Generic view for questionnaires."""

    form_class = None

    def get_questionnaire(self):
        """Return Questionnaire model for current form.

        The form is automatically generated based on the model instance.

        :return: related Questionnaire model
        :rtype: questionnaire_core.models.Questionnaire
        """
        raise NotImplementedError

    def get_questionnaire_result_set(self):
        """Return QuestionnaireResult model for current form.

        The results of the questionnaire are saved in the result set.

        Return an existing result set to allow editing
        or return a new (unsaved) model instance of QuestionnaireResult.

        :return: related QuestionnaireResult model
        :rtype: questionnaire_core.models.QuestionnaireResult
        """
        raise NotImplementedError

    def get_initial(self):
        return self.get_questionnaire_result_set().initial_form_data()

    def get_form_class(self):
        return self.get_questionnaire().build_form_class(self.get_questionnaire_result_set())

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
