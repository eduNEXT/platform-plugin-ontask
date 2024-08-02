"""
Courseware generalized definitions.
"""

from importlib import import_module

from django.conf import settings


def get_score(*args, **kwargs):
    """
    Wrapper for `openedx.lms.djangoapps.courseware.model_data.get_score`.
    """
    backend_function = settings.PLATFORM_PLUGIN_ONTASK_COURSEWARE_BACKEND
    backend = import_module(backend_function)

    return backend.get_score(*args, **kwargs)
