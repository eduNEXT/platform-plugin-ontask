"""Views for the OnTask plugin API."""

from logging import getLogger

from django.conf import settings
from django.http import HttpResponse
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from edx_rest_framework_extensions.auth.session.authentication import SessionAuthenticationAllowInactiveUser
from opaque_keys.edx.keys import CourseKey
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from platform_plugin_ontask.api.utils import (
    api_error,
    get_api_auth_token,
    get_course_block,
    get_course_key,
    get_workflow_id,
)
from platform_plugin_ontask.client import OnTaskClient
from platform_plugin_ontask.edxapp_wrapper.authentication import BearerAuthenticationAllowInactiveUser
from platform_plugin_ontask.edxapp_wrapper.modulestore import update_item
from platform_plugin_ontask.exceptions import (
    APIAuthTokenNotSetError,
    CourseNotFoundError,
    CustomInvalidKeyError,
    WorkflowIDNotSetError,
)
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
        try:
            course_block = get_course_block(get_course_key(course_id))
            api_auth_token = get_api_auth_token(course_block)

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
            course_block.other_course_settings["ONTASK_WORKFLOW_ID"] = created_workflow["id"]
            update_item(CourseKey.from_string(course_id), course_block, request.user.id)

            return Response(status=status.HTTP_201_CREATED)
        except (CustomInvalidKeyError, CourseNotFoundError, APIAuthTokenNotSetError) as error:
            return api_error(str(error), status_code=status.HTTP_400_BAD_REQUEST)


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
        try:
            course_block = get_course_block(get_course_key(course_id))
            api_auth_token = get_api_auth_token(course_block)
            workflow_id = get_workflow_id(course_block)

            upload_dataframe_to_ontask_task.delay(course_id, workflow_id, api_auth_token)

            return Response(status=status.HTTP_200_OK)

        except (CustomInvalidKeyError, CourseNotFoundError, APIAuthTokenNotSetError, WorkflowIDNotSetError) as error:
            return api_error(str(error), status_code=status.HTTP_400_BAD_REQUEST)
