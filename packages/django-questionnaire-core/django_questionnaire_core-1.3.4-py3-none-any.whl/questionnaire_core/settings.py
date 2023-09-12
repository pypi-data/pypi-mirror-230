from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import Storage
from django.utils.module_loading import import_string

from .question_types import QuestionTypeRegistry


upload_storage = None
upload_to_handler = None
upload_allowed_file_extensions = tuple()
active_question_types = list()

# validate & load QUESTIONNAIRE_CORE_UPLOAD_STORAGE
if getattr(settings, "QUESTIONNAIRE_CORE_UPLOAD_STORAGE", None):
    try:
        storage_class = import_string(getattr(settings, "QUESTIONNAIRE_CORE_UPLOAD_STORAGE"))
        upload_storage = storage_class()
        if not isinstance(upload_storage, Storage):
            raise ImproperlyConfigured(
                "User-defined QUESTIONNAIRE_CORE_UPLOAD_STORAGE is not a subclass of django.core.files.storage.Storage"
            )
    except ImportError:
        raise ImproperlyConfigured("Could not import user-defined QUESTIONNAIRE_CORE_UPLOAD_STORAGE")

# validate & load QUESTIONNAIRE_CORE_UPLOAD_TO_HANDLER
if getattr(settings, "QUESTIONNAIRE_CORE_UPLOAD_TO_HANDLER", None):
    try:
        upload_to_handler = import_string(getattr(settings, "QUESTIONNAIRE_CORE_UPLOAD_TO_HANDLER"))
        if not callable(upload_to_handler):
            raise ImproperlyConfigured("User-defined QUESTIONNAIRE_CORE_UPLOAD_TO_HANDLER is not callable.")
    except ImportError:
        raise ImproperlyConfigured("Could not import user-defined QUESTIONNAIRE_CORE_UPLOAD_TO_HANDLER")

# validate QUESTIONNAIRE_CORE_UPLOAD_ALLOWED_FILE_EXTENSIONS
if getattr(settings, "QUESTIONNAIRE_CORE_UPLOAD_ALLOWED_FILE_EXTENSIONS", None):
    if not isinstance(
        getattr(settings, "QUESTIONNAIRE_CORE_UPLOAD_ALLOWED_FILE_EXTENSIONS", list()),
        (list, tuple),
    ):
        raise ImproperlyConfigured(
            "User-defined QUESTIONNAIRE_CORE_UPLOAD_ALLOWED_FILE_EXTENSIONS must be a list or tuple."
        )
    else:
        upload_allowed_file_extensions = getattr(settings, "QUESTIONNAIRE_CORE_UPLOAD_ALLOWED_FILE_EXTENSIONS")

# validate & load QUESTIONNAIRE_CORE_ENABLED_QUESTION_TYPES
if getattr(settings, "QUESTIONNAIRE_CORE_ENABLED_QUESTION_TYPES", None):
    enable_types = getattr(settings, "QUESTIONNAIRE_CORE_ENABLED_QUESTION_TYPES")
    for enable_type in enable_types:
        if "." in enable_type:
            try:
                active_type = import_string(enable_type)
                active_question_types.append(active_type)
            except ImportError:
                raise ImproperlyConfigured("Could not import user-defined question type: {}".format(enable_type))
        else:
            active_type = QuestionTypeRegistry.get_question_type(enable_type)
            if active_type:
                active_question_types.append(active_type)
            else:
                raise ImproperlyConfigured("Invalid name for builtin question type: {}".format(enable_type))
else:
    # default: enable all builtin question types
    active_question_types = QuestionTypeRegistry.get_question_types().values()
