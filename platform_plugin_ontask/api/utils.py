"""Utility functions for the ELM credentials API."""

from __future__ import annotations

from collections import defaultdict

import requests
from django.conf import settings
from opaque_keys.edx.keys import CourseKey
from rest_framework.response import Response

from platform_plugin_ontask.edxapp_wrapper.completion import CompletionService
from platform_plugin_ontask.edxapp_wrapper.enrollments import get_user_enrollments
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


def get_course_units(course_key):
    """
    Extract a list of 'units' (verticals) from a course.

    Args:
        course_key (CourseKey): Course key.

    Returns:
        iterable: List of subsections.
    """
    course = modulestore().get_course(course_key, depth=0)
    for section in course.get_children():
        for subsection in section.get_children():
            yield from subsection.get_children()


def upload_dataframe_to_ontask(course_id: str, workflow_id: str, api_auth_token: str):
    """
    Upload a data frame to an OnTask

    Args:
        course_id (str): Course ID.
        workflow_id (str): OnTask workflow ID.
        api_auth_token (str): OnTask API authentication token.
    """
    course_key = CourseKey.from_string(course_id)
    enrollments = get_user_enrollments(course_id).filter(user__is_superuser=False, user__is_staff=False)
    course_units = list(get_course_units(course_key))
    data_frame = defaultdict(dict)

    index = 0
    for enrollment in enrollments:
        completion_service = CompletionService(enrollment.user, course_key)
        for unit in course_units:
            data_frame["id"][index] = index + 1
            data_frame["user_id"][index] = enrollment.user.id
            data_frame["email"][index] = enrollment.user.email
            data_frame["username"][index] = enrollment.user.username
            data_frame["course_id"][index] = course_id
            data_frame["block_id"][index] = unit.usage_key.block_id
            data_frame["block_name"][index] = unit.display_name
            data_frame["completed"][index] = completion_service.vertical_is_complete(unit)
            index += 1

    requests.put(
        url=f"{settings.ONTASK_INTERNAL_API}/table/{workflow_id}/ops/",
        json={"data_frame": data_frame},
        headers={"Authorization": f"Token {api_auth_token}"},
        timeout=5,
    )
