"""
Completion Service module generalized definitions.
"""

from importlib import import_module

from django.conf import settings


def init_completion_service(*args, **kwargs):
    """
    Wrapper for `completion.services.CompletionService`
    """
    backend_function = settings.PLATFORM_PLUGIN_ONTASK_COMPLETION_BACKEND
    backend = import_module(backend_function)

    return backend.CompletionService(*args, **kwargs)
