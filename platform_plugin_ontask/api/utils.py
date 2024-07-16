"""Utility functions for the OnTask plugin API."""

from __future__ import annotations

from importlib import import_module

from django.conf import settings
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from rest_framework.response import Response

from platform_plugin_ontask.datasummary.backends.base import DataSummary
from platform_plugin_ontask.datasummary.backends.completion import CompletionDataSummary
from platform_plugin_ontask.edxapp_wrapper.modulestore import modulestore
from platform_plugin_ontask.exceptions import (
    APIAuthTokenNotSetError,
    CourseNotFoundError,
    CustomInvalidKeyError,
    WorkflowIDNotSetError,
)

DEFAULT_DATA_SUMMARY_CLASS = CompletionDataSummary


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


def get_course_key(course_id: str) -> CourseKey:
    """
    Get the course key from the course ID.

    Args:
        course_id (str): Course ID.

    Raises:
        CustomInvalidKeyError: If the course key is not valid.

    Returns:
        CourseKey: The course key.
    """
    try:
        return CourseKey.from_string(course_id)
    except InvalidKeyError as exc:
        raise CustomInvalidKeyError() from exc


def get_course_block(course_key: CourseKey):
    """
    Get the course block from the course key.

    Args:
        course_key (CourseKey): The course key.

    Raises:
        CourseNotFoundError: If the course is not found.

    Returns:
        CourseBlock: The course block.
    """
    course_block = modulestore().get_course(course_key)
    if course_block is None:
        raise CourseNotFoundError()
    return course_block


def get_api_auth_token(course_block) -> str:
    """
    Get the OnTask API Auth Token from the other course settings.

    Args:
        course_block (CourseBlock): The course block.

    Raises:
        APIAuthTokenNotSetError: If the OnTask API Auth Token is not set.

    Returns:
        str: The OnTask API Auth Token.
    """
    api_auth_token = course_block.other_course_settings.get("ONTASK_API_AUTH_TOKEN")
    if api_auth_token is None:
        raise APIAuthTokenNotSetError()
    return api_auth_token


def get_workflow_id(course_block) -> str:
    """
    Get the OnTask workflow ID from the other course settings.

    Args:
        course_block (CourseBlock): The course block.

    Raises:
        WorkflowIDNotSetError: If the OnTask workflow ID is not set.

    Returns:
        str: The OnTask workflow ID.
    """
    workflow_id = course_block.other_course_settings.get("ONTASK_WORKFLOW_ID")
    if workflow_id is None:
        raise WorkflowIDNotSetError()
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
