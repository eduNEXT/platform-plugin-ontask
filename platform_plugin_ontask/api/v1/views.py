"""Views for the OnTask plugin API."""

from copy import deepcopy
from logging import getLogger

from django.conf import settings
from django.http import HttpResponse
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from edx_rest_framework_extensions.auth.session.authentication import SessionAuthenticationAllowInactiveUser
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from platform_plugin_ontask.api.utils import (
    api_error,
    get_course_block_by_course_id,
    validate_api_auth_token,
    validate_workflow_id,
)
from platform_plugin_ontask.client import OnTaskClient
from platform_plugin_ontask.edxapp_wrapper.authentication import BearerAuthenticationAllowInactiveUser
from platform_plugin_ontask.edxapp_wrapper.modulestore import modulestore
from platform_plugin_ontask.tasks import upload_dataframe_to_ontask_task

log = getLogger(__name__)


class OnTaskWorkflowAPIView(APIView):
    """
    API view for managing OnTask Workflows.

    `Use Cases`:

        * POST: Create a new OnTask workflow for the course.

    `Example Requests`:

        * POST platform-plugin-ontask/{course_id}/api/v1/workflow/

            * Path Parameters:
                * course_id (str): The unique identifier for the course (required).

    `Example Response`:

        * POST platform-plugin-ontask/{course_id}/api/v1/workflow/

            * 201: The OnTask workflow is created successfully.

            * 400:
                * The supplied course_id key is not valid.
                * The OnTask API Auth token is not set.

            * 404: The course is not found.
    """

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
        course_block = get_course_block_by_course_id(course_id)
        if isinstance(course_block, Response):
            return course_block

        api_auth_token = validate_api_auth_token(course_block)
        if isinstance(api_auth_token, Response):
            return api_auth_token

        ontask_client = OnTaskClient(settings.ONTASK_INTERNAL_API, api_auth_token)
        response = ontask_client.create_workflow(course_id)

        if not response.ok:
            log.error(f"POST {response.url} | status-code={response.status_code} | response={response.text}")
            return api_error(
                "An error occurred while creating the workflow. Ensure the "
                "workflow for this course does not already exist, and that the "
                "OnTask API Auth token is correct.",
                status_code=response.status_code,
            )

        created_workflow = response.json()

        other_course_settings = deepcopy(course_block.other_course_settings)
        other_course_settings["ONTASK_WORKFLOW_ID"] = created_workflow["id"]
        course_block.other_course_settings = other_course_settings
        modulestore().update_item(course_block, request.user.id)

        return Response(status=status.HTTP_201_CREATED)


class OnTaskTableAPIView(APIView):
    """
    API view for managing OnTask Tables.

    `Use Cases`:

        * PUT: Upload the course data to OnTask.

    `Example Requests`:

        * PUT platform-plugin-ontask/{course_id}/api/v1/table/

            * Path Parameters:

                * course_id (str): The unique identifier for the course (required).

    `Example Response`:

        * PUT platform-plugin-ontask/{course_id}/api/v1/table/

            * 200: The course data is uploaded to OnTask successfully.

            * 400:
                * The supplied course_id key is not valid.
                * The OnTask API Auth token is not set.
                * The OnTask Workflow ID is not set.

            * 404: The course is not found.
    """

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
        course_block = get_course_block_by_course_id(course_id)
        if isinstance(course_block, Response):
            return course_block

        api_auth_token = validate_api_auth_token(course_block)
        if isinstance(api_auth_token, Response):
            return api_auth_token

        workflow_id = validate_workflow_id(course_block)
        if isinstance(workflow_id, Response):
            return workflow_id

        upload_dataframe_to_ontask_task.delay(course_id, workflow_id, api_auth_token)

        return Response(status=status.HTTP_200_OK)
