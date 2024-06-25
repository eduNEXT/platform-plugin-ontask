"""Views for the OnTask plugin API."""

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

from platform_plugin_ontask.api.utils import api_error, api_field_errors, get_course_sequences
from platform_plugin_ontask.edxapp_wrapper.authentication import BearerAuthenticationAllowInactiveUser
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

        # course_subsections = get_course_sequences(course_key)
        completion_service = CompletionService(request.user, course_key)

        course_block = modulestore().get_course(course_key)
        if course_block is None:
            return api_field_errors(
                {"course_id": f"The course with {course_id=} is not found."},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        api_auth_token = course_block.other_course_settings.get("ONTASK_API_AUTH_TOKEN")
        workflow_id = course_block.other_course_settings.get("ONTASK_WORKFLOW_ID")

        current_table = requests.get(
            url=f"{settings.ONTASK_INTERNAL_API}/table/{workflow_id}/ops/",
            headers={"Authorization": f"Token {api_auth_token}"},
            timeout=5,
        ).json()

        if current_table["data_frame"] is None:
            new_table_response = requests.put(
                url=f"{settings.ONTASK_INTERNAL_API}/table/{workflow_id}/ops/",
                json={
                    "data_frame": {
                        "user_id": {"0": 1, "1": "2"},
                        "course_id": {"0": "course-v1:edunext+ontask+demo", "1": "course-v1:edunext+ontask+demo"},
                        "aggregated_completion_data": {"0": "test-data-1", "1": "test-data-2"},
                    }
                },
                headers={"Authorization": f"Token {api_auth_token}"},
                timeout=5,
            )

            if new_table_response.status_code != status.HTTP_201_CREATED:
                return api_error(
                    {"detail": "An error occurred while creating the data frame"},
                    status_code=new_table_response.status_code,
                )

        aggregated_completion = AgregationCompletionData(completion_service)
        new_data = aggregated_completion.get_agregation_completion_data()

        requests.put(
            url=f"{settings.ONTASK_INTERNAL_API}/table/{workflow_id}/merge/",
            json={"how": "outer", "left_on": "user_id", "right_on": "user_id", "src_df": new_data},
            headers={"Authorization": f"Token {api_auth_token}"},
            timeout=5,
        )

        return Response({"created_data_frame": False, "data_frame": current_table["data_frame"]})

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

        course_block.other_course_settings["ONTASK_WORKFLOW_ID"] = created_workflow["id"]
        modulestore().update_item(course_block, request.user.id)

        return Response({"workflow": created_workflow})


class AgregationCompletionData:
    """Agregate the completion data of a user in a course."""

    def __init__(self, completion_service: CompletionService):
        self.completion_service = completion_service.get_completions()

    def get_agregation_completion_data(self):
        return {
            "user_id": {"0": 1, "1": "2"},
            "course_id": {"0": "course-v1:edunext+ontask+demo", "1": "course-v1:edunext+ontask+demo"},
            "aggregated_completion_data": {"0": "test-data-1", "1": "test-data-2"},
        }
