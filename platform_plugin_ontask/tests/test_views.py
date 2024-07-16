"""Tests for the API views of the OnTask plugin."""

from unittest.mock import Mock, patch

from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from platform_plugin_ontask.api.v1.views import OnTaskTableAPIView, OnTaskWorkflowAPIView

VIEWS_MODULE_PATH = "platform_plugin_ontask.api.v1.views"
UTILS_MODULE_PATH = "platform_plugin_ontask.api.utils"

modulestore_patch = patch(f"{UTILS_MODULE_PATH}.modulestore")
request_post_patch = patch(f"{VIEWS_MODULE_PATH}.requests.post")
task_patch = patch(f"{VIEWS_MODULE_PATH}.upload_dataframe_to_ontask_task.delay")
create_workflow_patch = patch(f"{VIEWS_MODULE_PATH}.OnTaskClient.create_workflow")


class OnTaskWorkflowAPIViewTest(APITestCase):
    """Tests for the OnTaskWorkflowAPIView."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = OnTaskWorkflowAPIView.as_view()
        self.url = reverse("api:v1:workflow")

        self.request_user = Mock()
        self.request_user.is_staff = True

        self.course_id = "course-v1:edX+DemoX+Demo_Course"
        self.other_course_settings = {
            "ONTASK_API_AUTH_TOKEN": "ontask-api-auth-token",
            "ONTASK_WORKFLOW_ID": "ontask-workflow-id",
        }
        self.course = Mock(id=self.course_id, other_course_settings=self.other_course_settings)

    def post_request(self):
        """Return a POST request."""
        request = self.factory.post(self.url)
        force_authenticate(request, user=self.request_user)
        return self.view(request, course_id=self.course_id)

    @override_settings(ONTASK_INTERNAL_API="http://ontask:8080")
    @create_workflow_patch
    @modulestore_patch
    def test_create_workflow(self, modulestore_mock: Mock, create_workflow_mock: Mock):
        """Test POST request for creating a new workflow in OnTask."""
        modulestore_mock.return_value.get_course.return_value = self.course
        create_workflow_mock.return_value = Mock(
            status_code=status.HTTP_201_CREATED, json=lambda: {"id": "new_workflow_id"}
        )

        response = self.post_request()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_workflow_invalid_course_key(self):
        """Test POST request for creating a new workflow with invalid course key."""
        self.course_id = "invalid_course_key"

        response = self.post_request()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "The course key is not valid.")

    @modulestore_patch
    def test_create_workflow_course_not_found(self, modulestore_mock: Mock):
        """Test POST request for creating a new workflow with course not found."""
        modulestore_mock.return_value.get_course.return_value = None

        response = self.post_request()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "The course does not exist.")

    @modulestore_patch
    def test_create_workflow_missing_auth_token(self, modulestore_mock: Mock):
        """Test POST request for creating a new workflow with missing auth token."""
        self.course.other_course_settings = {}
        modulestore_mock.return_value.get_course.return_value = self.course

        response = self.post_request()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"],
            "The OnTask API Auth Token is not set for this course. "
            "Please set it in the Advanced Settings of the course.",
        )

    @override_settings(ONTASK_INTERNAL_API="http://ontask:8080")
    @create_workflow_patch
    @modulestore_patch
    def test_create_workflow_external_api_failure(self, modulestore_mock: Mock, create_workflow_mock: Mock):
        """Test POST request for creating a new workflow with external API failure."""
        modulestore_mock.return_value.get_course.return_value = self.course
        create_workflow_mock.return_value = Mock(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, ok=False)

        response = self.post_request()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"],
            "An error occurred while creating the workflow. Ensure the "
            "workflow for this course does not already exist, and that the "
            "OnTask API Auth token is correct.",
        )


class OnTaskTableAPIViewTest(APITestCase):
    """Tests for the OnTaskTableAPIView."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = OnTaskTableAPIView.as_view()
        self.url = reverse("api:v1:table")

        self.request_user = Mock()
        self.request_user.is_staff = True

        self.course_id = "course-v1:edX+DemoX+Demo_Course"
        self.other_course_settings = {
            "ONTASK_API_AUTH_TOKEN": "ontask-api-auth-token",
            "ONTASK_WORKFLOW_ID": "ontask-workflow-id",
        }
        self.course = Mock(id=self.course_id, other_course_settings=self.other_course_settings)
        self.mock_response = Mock(status_code=status.HTTP_201_CREATED, json=lambda: {"id": "new_workflow_id"})

    def put_request(self):
        """Return a PUT request."""
        request = self.factory.put(self.url)
        force_authenticate(request, user=self.request_user)
        return self.view(request, course_id=self.course_id)

    @task_patch
    @modulestore_patch
    def test_upload_dataframe(self, modulestore_mock: Mock, task_mock: Mock):
        """Test PUT request for uploading a dataframe to OnTask."""
        modulestore_mock.return_value.get_course.return_value = self.course
        task_mock.return_value = None

        response = self.put_request()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_upload_dataframe_invalid_course_key(self):
        """Test PUT request for uploading a dataframe with invalid course key."""
        self.course_id = "invalid_course_key"

        response = self.put_request()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "The course key is not valid.")

    @modulestore_patch
    def test_upload_dataframe_course_not_found(self, modulestore_mock: Mock):
        """Test PUT request for uploading a dataframe with course not found."""
        modulestore_mock.return_value.get_course.return_value = None

        response = self.put_request()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "The course does not exist.")

    @modulestore_patch
    def test_upload_dataframe_missing_api_auth_token(self, modulestore_mock: Mock):
        """Test PUT request for uploading a dataframe with missing auth token."""
        self.course.other_course_settings = {}
        modulestore_mock.return_value.get_course.return_value = self.course

        response = self.put_request()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"],
            "The OnTask API Auth Token is not set for this course. "
            "Please set it in the Advanced Settings of the course.",
        )

    @modulestore_patch
    def test_upload_dataframe_missing_workflow_id(self, modulestore_mock: Mock):
        """Test PUT request for uploading a dataframe with missing workflow ID."""
        self.course.other_course_settings = {"ONTASK_API_AUTH_TOKEN": "ontask-api-auth-token"}
        modulestore_mock.return_value.get_course.return_value = self.course

        response = self.put_request()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"],
            "The OnTask Workflow ID is not set for this course. Please set "
            "it in the Advanced Settings of the course.",
        )
