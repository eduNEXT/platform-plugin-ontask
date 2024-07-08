"""Utility functions for the OnTask plugin API."""

from __future__ import annotations

from importlib import import_module

from django.conf import settings
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from rest_framework import status
from rest_framework.response import Response

from platform_plugin_ontask.datasummary.backends.base import DataSummary
from platform_plugin_ontask.datasummary.backends.completion import CompletionDataSummary
from platform_plugin_ontask.edxapp_wrapper.modulestore import modulestore

DEFAULT_DATA_SUMMARY_CLASS = CompletionDataSummary


def api_error(error: dict | str, status_code: int) -> Response:
    """
    Build a response with an error.

    Args:
        error (dict | str): Error to return.
        status_code (int): Status code to return.

    Returns:
        Response: Response with an error.
    """
    return Response(data={"error": error}, status=status_code)


def get_course_block_by_course_id(course_id: str):
    """
    Get the course block by course ID.

    Args:
        course_id (str): Course ID.

    Returns:
        CourseBlock | Response: The course block if it exists, or a response with
            an error if it does not exist.
    """
    try:
        course_key = CourseKey.from_string(course_id)
    except InvalidKeyError:
        return api_error(
            {"course_id": f"The supplied {course_id=} key is not valid."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    course_block = modulestore().get_course(course_key)
    if course_block is None:
        return api_error(
            {"course_id": f"The course with {course_id=} does not exist."},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return course_block


def validate_api_auth_token(course_block) -> str | Response:
    """
    Validate the OnTask API Auth Token for the course.

    If the token is not set, it returns a response with an error.
    If the token is set, it returns the token.

    Args:
        course_block (CourseBlock): The course block.

    Returns:
        str | Response: The API Auth Token if it is set, or a response with an error.
    """
    api_auth_token = course_block.other_course_settings.get("ONTASK_API_AUTH_TOKEN")

    if api_auth_token is None:
        return api_error(
            "The OnTask API Auth Token is not set for this course. "
            "Please set it in the Advanced Settings of the course.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return api_auth_token


def validate_workflow_id(course_block) -> str | Response:
    """
    Validate the OnTask workflow ID.

    If the workflow ID is not set, it returns a response with an error.
    If the workflow ID is set, it returns the workflow ID.

    Args:
        course_block (CourseBlock): The course block.

    Returns:
        str | Response: The workflow ID if it is set, or a response with an error.
    """
    workflow_id = course_block.other_course_settings.get("ONTASK_WORKFLOW_ID")

    if workflow_id is None:
        return api_error(
            "The OnTask Workflow ID is not set for this course. Please set "
            "it in the Advanced Settings of the course or create a new workflow.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return workflow_id


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
        return DEFAULT_DATA_SUMMARY_CLASS

    module_name, class_name = data_summary_class.rsplit(".", 1)
    module = import_module(module_name)

    return getattr(module, class_name, DEFAULT_DATA_SUMMARY_CLASS)
