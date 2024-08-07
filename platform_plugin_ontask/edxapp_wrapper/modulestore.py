"""
Modulestore generalized definitions.
"""

from importlib import import_module

from django.conf import settings


def modulestore(*args, **kwargs):
    """
    Wrapper for `xmodule.modulestore.django.modulestore`
    """
    backend_function = settings.PLATFORM_PLUGIN_ONTASK_MODULESTORE_BACKEND
    backend = import_module(backend_function)

    return backend.modulestore(*args, **kwargs)


def update_item(*args, **kwargs):
    """
    Wrapper for `xmodule.modulestore.django.modulestore.update_item`
    """
    backend_function = settings.PLATFORM_PLUGIN_ONTASK_MODULESTORE_BACKEND
    backend = import_module(backend_function)

    return backend.update_item(*args, **kwargs)
