"""Utility functions for the OnTask plugin API."""

from __future__ import annotations

import logging
from importlib import import_module

from django.conf import settings
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from requests import Response

from platform_plugin_ontask.data_summary.backends.base import DataSummary
from platform_plugin_ontask.edxapp_wrapper.modulestore import modulestore
from platform_plugin_ontask.exceptions import (
    APIAuthTokenNotSetError,
    CourseNotFoundError,
    CustomInvalidKeyError,
    WorkflowIDNotSetError,
)

log = logging.getLogger(__name__)


def ontask_log_from_response(response: Response) -> str:
    """
    Return a log message from a response object.

    Arguments:
        response (Response): The response object.
    """
    return (
        f"{response.request.method} {response.url} | "
        f"status-code={response.status_code} | "
        f"response={response.text}",
    )


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
    Get the OnTask API Auth Token.

    First, it tries to get the token from the django settings. If it is not set,
    it tries to get it from the other course settings.

    Args:
        course_block (CourseBlock): The course block.

    Raises:
        APIAuthTokenNotSetError: If the OnTask API Auth Token is not set.

    Returns:
        str: The OnTask API Auth Token.
    """
    api_auth_token = getattr(settings, "ONTASK_API_AUTH_TOKEN", None) or course_block.other_course_settings.get(
        "ONTASK_API_AUTH_TOKEN"
    )
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


def get_data_summary_class(data_summary_class_path: str) -> DataSummary | None:
    """
    Get the data summary class based on the module path.

    Returns:
        DataSummary | None: The class to be used to generate the data summary.
            If the class is not found, it returns None.
    """
    module_name, class_name = data_summary_class_path.rsplit(".", 1)
    try:
        module = import_module(module_name)
        return getattr(module, class_name)
    except ImportError:
        return None
