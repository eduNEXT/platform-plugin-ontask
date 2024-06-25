"""Utility functions for the ELM credentials API."""

from __future__ import annotations

from rest_framework.response import Response

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


def api_error(error: str | dict, status_code: int) -> Response:
    """
    Build a response with an error.

    Args:
        error (str | dict): Error to return.
        status_code (int): Status code to return.

    Returns:
        Response: Response with an error.
    """
    return Response(data={"error": error}, status=status_code)


def get_course_sequences(course_key):
    """
    Extract a list of 'subsections' from a course.

    Args:
        course_key (CourseKey): Course key.

    Returns:
        iterable: List of subsections.
    """
    course = modulestore().get_course(course_key, depth=0)
    for section in course.get_children():
        for subsection in section.get_children():
            yield from subsection.get_children()
