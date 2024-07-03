"""Views for the OnTask plugin API."""

from copy import deepcopy

import requests
from django.conf import settings
from django.http import HttpResponse
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from edx_rest_framework_extensions.auth.session.authentication import SessionAuthenticationAllowInactiveUser
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from platform_plugin_ontask.api.utils import api_error, api_field_errors
from platform_plugin_ontask.edxapp_wrapper.authentication import BearerAuthenticationAllowInactiveUser
from platform_plugin_ontask.edxapp_wrapper.modulestore import modulestore
from platform_plugin_ontask.tasks import upload_dataframe_to_ontask_task


class OnTaskWorkflowAPIView(APIView):
    """View to manage OnTask Workflows."""

    authentication_classes = (
        JwtAuthentication,
        BearerAuthenticationAllowInactiveUser,
        SessionAuthenticationAllowInactiveUser,
    )
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, course_id: str) -> HttpResponse:
        """
        Handle POST requests to set the OnTask workflow ID.

        Arguments:
            request (Request): The HTTP request object.
            course_id (str): The course ID.

        Returns:
            HttpResponse: The response object.
        """
        try:
            course_key = CourseKey.from_string(course_id)
        except InvalidKeyError:
            return api_field_errors(
                {"course_id": f"The supplied {course_id=} key is not valid."},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        course_block = modulestore().get_course(course_key)
        if course_block is None:
            return api_field_errors(
                {"course_id": f"The course with {course_id=} is not found."},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        api_auth_token = course_block.other_course_settings.get("ONTASK_API_AUTH_TOKEN")

        if api_auth_token is None:
            return api_error(
                "The OnTask API Auth Token is not set for this course. "
                "Please set it in the Advanced Settings of the course.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        created_workflow_response = requests.post(
            url=f"{settings.ONTASK_INTERNAL_API}/workflow/workflows/",
            json={"name": course_id},
            headers={"Authorization": f"Token {api_auth_token}"},
            timeout=5,
        )
        created_workflow = created_workflow_response.json()

        if created_workflow_response.status_code != status.HTTP_201_CREATED:
            return api_error(
                "An error occurred while creating the workflow. Ensure the "
                "workflow for this course does not already exist, and that the "
                "OnTask API Auth token is correct.",
                status_code=created_workflow_response.status_code,
            )

        other_course_settings = deepcopy(course_block.other_course_settings)
        other_course_settings["ONTASK_WORKFLOW_ID"] = created_workflow["id"]
        course_block.other_course_settings = other_course_settings
        modulestore().update_item(course_block, request.user.id)

        return Response({"success": True}, status=status.HTTP_201_CREATED)


class OnTaskTableAPIView(APIView):
    """View to manage OnTask Tables."""

    authentication_classes = (
        JwtAuthentication,
        BearerAuthenticationAllowInactiveUser,
        SessionAuthenticationAllowInactiveUser,
    )
    permission_classes = (permissions.IsAuthenticated,)

    def put(self, _, course_id: str) -> HttpResponse:
        """
        Handle PUT requests to upload the course data to OnTask.

        The course data is uploaded to the OnTask table in the workflow.

        Arguments:
            _ (Request): The HTTP request object.
            course_id (str): The course ID.

        Returns:
            HttpResponse: The response object.
        """
        try:
            course_key = CourseKey.from_string(course_id)
        except InvalidKeyError:
            return api_field_errors(
                {"course_id": f"The supplied {course_id=} key is not valid."},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        course_block = modulestore().get_course(course_key)
        if course_block is None:
            return api_field_errors(
                {"course_id": f"The course with {course_id=} is not found."},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        api_auth_token = course_block.other_course_settings.get("ONTASK_API_AUTH_TOKEN")
        workflow_id = course_block.other_course_settings.get("ONTASK_WORKFLOW_ID")

        if api_auth_token is None or workflow_id is None:
            return api_error(
                "The OnTask API Auth Token or Workflow ID is not set for this course.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        upload_dataframe_to_ontask_task.delay(course_id, workflow_id, api_auth_token)

        return Response({"sucess": True})
