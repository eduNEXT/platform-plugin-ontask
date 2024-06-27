"""Views for the OnTask plugin API."""

from collections import defaultdict
from copy import deepcopy

import requests
from completion.services import CompletionService
from django.conf import settings
from django.http import HttpResponse
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from edx_rest_framework_extensions.auth.session.authentication import SessionAuthenticationAllowInactiveUser
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from platform_plugin_ontask.api.utils import api_error, api_field_errors, get_course_units
from platform_plugin_ontask.edxapp_wrapper.authentication import BearerAuthenticationAllowInactiveUser
from platform_plugin_ontask.edxapp_wrapper.enrollments import get_user_enrollments
from platform_plugin_ontask.edxapp_wrapper.modulestore import modulestore


class OntaskWorkflowView(APIView):
    """View to manage OnTask Workflows."""

    authentication_classes = (
        JwtAuthentication,
        BearerAuthenticationAllowInactiveUser,
        SessionAuthenticationAllowInactiveUser,
    )
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request, course_id: str) -> HttpResponse:
        """
        Handle PATCH requests to update the OnTask workflow ID.

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
        workflow_id = course_block.other_course_settings.get("ONTASK_WORKFLOW_ID")

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

        table_response = requests.put(
            url=f"{settings.ONTASK_INTERNAL_API}/table/{workflow_id}/ops/",
            json={"data_frame": data_frame},
            headers={"Authorization": f"Token {api_auth_token}"},
            timeout=5,
        )

        if table_response.status_code != status.HTTP_201_CREATED:
            return api_error(
                {"detail": "An error occurred while creating the data frame"},
                status_code=table_response.status_code,
            )

        return Response({"sucess": True})

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
                {
                    "detail": (
                        "An error occurred while creating the workflow. Ensure the "
                        "workflow for this course does not already exist."
                    ),
                    "ontask_api_error": created_workflow,
                },
                status_code=created_workflow_response.status_code,
            )

        other_course_settings = deepcopy(course_block.other_course_settings)
        other_course_settings["ONTASK_WORKFLOW_ID"] = created_workflow["id"]
        course_block.other_course_settings = other_course_settings
        modulestore().update_item(course_block, request.user.id)

        return Response({"workflow": created_workflow})
