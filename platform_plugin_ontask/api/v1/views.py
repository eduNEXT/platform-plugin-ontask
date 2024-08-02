"""Views for the OnTask plugin API."""

import logging

from django.conf import settings
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from edx_rest_framework_extensions.auth.session.authentication import SessionAuthenticationAllowInactiveUser
from opaque_keys.edx.keys import CourseKey
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from platform_plugin_ontask.api.utils import (
    get_api_auth_token,
    get_course_block,
    get_course_key,
    get_workflow_id,
)
from platform_plugin_ontask.client import OnTaskClient
from platform_plugin_ontask.edxapp_wrapper.authentication import BearerAuthenticationAllowInactiveUser
from platform_plugin_ontask.edxapp_wrapper.enrollments import get_user_enrollments
from platform_plugin_ontask.edxapp_wrapper.modulestore import update_item
from platform_plugin_ontask.exceptions import (
    APIAuthTokenNotSetError,
    CourseNotFoundError,
    CustomInvalidKeyError,
    WorkflowIDNotSetError,
)
from platform_plugin_ontask.tasks import upload_dataframe_to_ontask_task

log = logging.getLogger(__name__)


class OnTaskWorkflowAPIView(APIView):
    """
    API view for managing OnTask Workflows.

    `Use Cases`:

        * POST: Create a new OnTask workflow for the course. Also, create a
            table in the workflow with the enrollment data.

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
                * The course does not exist.
    """

    authentication_classes = (
        JwtAuthentication,
        BearerAuthenticationAllowInactiveUser,
        SessionAuthenticationAllowInactiveUser,
    )
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, course_id: str) -> Response:
        """
        Handle POST requests to create a new OnTask workflow for the course.

        The workflow ID is stored in the Other Course Settings of the course.
        A table is created in the workflow with the enrollment data.

        Arguments:
            request (Request): The HTTP request object.
            course_id (str): The course ID.

        Returns:
            Response: The response object.
        """
        try:
            course_block = get_course_block(get_course_key(course_id))
            api_auth_token = get_api_auth_token(course_block)

            ontask_client = OnTaskClient(settings.ONTASK_INTERNAL_API, api_auth_token)
            create_workflow_response = ontask_client.create_workflow(course_id)

            if not create_workflow_response.ok:
                log.error(create_workflow_response.text)
                return Response(
                    data={
                        "error": "An error occurred while creating the workflow. "
                        "Ensure the workflow for this course does not already "
                        "exist, and that the OnTask API Auth token is correct."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            workflow_id = create_workflow_response.json()["id"]
            course_block.other_course_settings["ONTASK_WORKFLOW_ID"] = workflow_id
            update_item(CourseKey.from_string(course_id), course_block, request.user.id)

            enrollments = get_user_enrollments(course_id)
            data_frame = {"user_id": {}}
            for index, enrollment in enumerate(enrollments):
                data_frame["user_id"][index] = enrollment.user.id

            update_table_response = ontask_client.update_table(workflow_id, data_frame)

            if not update_table_response.ok:
                log.error(update_table_response.text)
                return Response(
                    data={
                        "error": "An error occurred while updating the table. "
                        "Ensure the workflow for this course exists, and that "
                        "the OnTask API Auth token is correct."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(status=status.HTTP_201_CREATED)
        except (CustomInvalidKeyError, CourseNotFoundError, APIAuthTokenNotSetError) as error:
            return Response(data={"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)


class OnTaskTableAPIView(APIView):
    """
    API view for managing OnTask Tables.

    `Use Cases`:

        * PUT: Upload the course data to OnTask. This merge the new data with
            the existing data in the table.

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
                * The course does not exist.
    """

    authentication_classes = (
        JwtAuthentication,
        BearerAuthenticationAllowInactiveUser,
        SessionAuthenticationAllowInactiveUser,
    )
    permission_classes = (permissions.IsAuthenticated,)

    def put(self, _, course_id: str) -> Response:
        """
        Handle PUT requests to upload the course data to OnTask.

        The course data is uploaded to the OnTask table in the workflow.

        Arguments:
            _ (Request): The HTTP request object.
            course_id (str): The course ID.

        Returns:
            Response: The response object.
        """
        try:
            course_block = get_course_block(get_course_key(course_id))
            api_auth_token = get_api_auth_token(course_block)
            workflow_id = get_workflow_id(course_block)

            upload_dataframe_to_ontask_task.delay(course_id, workflow_id, api_auth_token)

            return Response(status=status.HTTP_200_OK)

        except (CustomInvalidKeyError, CourseNotFoundError, APIAuthTokenNotSetError, WorkflowIDNotSetError) as error:
            return Response(data={"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
