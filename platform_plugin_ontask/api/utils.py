"""Utility functions for the OnTask plugin."""

from __future__ import annotations

from importlib import import_module
from typing import Iterable

from django.conf import settings
from rest_framework.response import Response

from platform_plugin_ontask.datasummary.backends.base import DataSummary
from platform_plugin_ontask.datasummary.backends.completion import CompletionDataSummary
from platform_plugin_ontask.edxapp_wrapper.modulestore import modulestore


def api_field_errors(field_errors: dict, status_code: int) -> Response:
    """
    Build a response with field errors.

    Args:
        field_errors (dict): Errors to return.
        status_code (int): Status code to return.

    Returns:
        Response: Response with field errors.
    """
    return Response(data={"field_errors": field_errors}, status=status_code)


def api_error(error: str, status_code: int) -> Response:
    """
    Build a response with an error.

    Args:
        error (str): Error to return.
        status_code (int): Status code to return.

    Returns:
        Response: Response with an error.
    """
    return Response(data={"error": error}, status=status_code)


def get_course_units(course_key) -> Iterable:
    """
    Extract a list of 'units' (verticals) from a course.

    Args:
        course_key (CourseKey): Course key.

    Returns:
        Iterable: List of units.
    """
    course = modulestore().get_course(course_key, depth=0)
    for section in course.get_children():
        for subsection in section.get_children():
            yield from subsection.get_children()


def get_data_summary_class() -> DataSummary:
    """
    Get the data summary class based on django settings.

    This function retrieves the data summary class to be used based
    on the value of the `ONTASK_DATA_SUMMARY_CLASS` django setting.
    If the variable is not set or is empty, it returns the default
    data summary class `CompletionDataSummary`.

    Returns:
        DataSummary: The class to be used to generate the data summary.
    """
    data_summary_class = getattr(settings, "ONTASK_DATA_SUMMARY_CLASS", None)

    if not data_summary_class:
        return CompletionDataSummary

    module_name, class_name = data_summary_class.rsplit(".", 1)
    module = import_module(module_name)

    return getattr(module, class_name, CompletionDataSummary)
