"""
Completion Service module generalized definitions.
"""

from importlib import import_module

from django.conf import settings


def get_completion_service_class():
    """
    Wrapper for `completion.services.CompletionService`
    """
    backend_function = settings.PLATFORM_PLUGIN_ONTASK_COMPLETION_BACKEND
    backend = import_module(backend_function)

    return backend.CompletionService


CompletionService = get_completion_service_class()
