"""Views for the OnTask plugin API."""

import requests
from django.http import HttpResponse
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from edx_rest_framework_extensions.auth.session.authentication import SessionAuthenticationAllowInactiveUser
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from platform_plugin_ontask.api.utils import api_field_errors
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

    def post(self, request, course_id) -> HttpResponse:
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

        created_workflow = requests.post(
            url="http://ontask:8080/workflow/workflows/",
            json={"name": f"Workflow of {course_id}"},
            headers={"Authorization": "Token 4ca7789071b6f53ea38ce3e309dadbf473840f5a"},
            timeout=5,
        ).json()

        course_block.other_course_settings["ontaskWorkflowId"] = created_workflow["id"]
        modulestore().update_item(course_block, request.user.id)

        return Response({"workflow": created_workflow})
