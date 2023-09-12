# django-questionnaire-core

A django application which can be used as a base / starting point for questionnaire functionality in your project.
It heavily relies on django form fields & widgets and uses PostgreSQL JSON fields to store the results.

## Requirements

- Python version 3.6+
- [Django](https://www.djangoproject.com) version 2.2+
- [django-ordered-model](https://github.com/bfirsh/django-ordered-model)
- A [PostgreSQL](https://www.postgresql.org/) Database


## Quick start

1. Add "questionnaire_core" and its dependency to your INSTALLED_APPS setting like this:

    ```
    INSTALLED_APPS = [
        ...
        'ordered_model',
        'questionnaire_core',
    ]
    ```

2. Create a view based on `questionnaire_core.views.generic.QuestionnaireFormView`; a simple version might look like this:

    ```python
    from django.http import HttpResponseRedirect
    from django.urls import reverse
    from django.utils.http import urlencode

    from questionnaire_core.models import Questionnaire, QuestionnaireResult
    from questionnaire_core.views.generic import QuestionnaireFormView

    class BasicQuestionnaireView(QuestionnaireFormView):
        template_name = 'basic_questionnaire.html'

        def get_questionnaire(self):
            return Questionnaire.objects.get(pk=self.kwargs.get('pk'))

        def get_questionnaire_result_set(self):
            if self.request.GET.get('result_set'):
                return QuestionnaireResult.objects.get(pk=self.request.GET.get('result_set'))
            return QuestionnaireResult(questionnaire=self.get_questionnaire())

        def get_success_url(self):
            return reverse('basic_questionnaire', args=(self.kwargs.get('pk'),))

        def form_valid(self, form):
            # Add current result set to the url (allows editing of the result)
            redirect = super().form_valid(form)
            url_params = urlencode({'result_set': form.current_result_set.pk})
            return HttpResponseRedirect('{url}?{params}'.format(url=redirect.url, params=url_params))

    ```

3. Add the new view to your URLconf:

    ```
    path('questionnaire/<int:pk>/', BasicQuestionnaireView.as_view(), name='basic_questionnaire'),
    ```

4. Run `python manage.py migrate` to create the questionnaire_core models.

5. Start the development server and visit http://127.0.0.1:8000/admin/
    to create a questionnaire (you'll need the Admin app enabled).

6. Visit http://127.0.0.1:8000/questionnaire/1/ to test your first questionnaire.


## Development setup

1. Upgrade packaging tools:

    ```bash
    python -m pip install --upgrade pip
    python -m pip install --upgrade setuptools wheel
    ```

2. Install Django (the `example_app` expects django 3.1):

    ```bash
    python -m pip install Django~=3.1.0 django-ordered-model psycopg2
    ```

3. Install tox, isort & flake8

    ```bash
    python -m pip install tox isort flake8
    ```
