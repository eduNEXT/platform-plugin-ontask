"""Tests for the tasks module of the OnTask plugin."""

from unittest import TestCase
from unittest.mock import Mock, patch

from django.conf import settings
from django.test import override_settings
from rest_framework import status

from platform_plugin_ontask.tasks import upload_dataframe_to_ontask_task

TASKS_MODULE_PATH = "platform_plugin_ontask.tasks"


class TestUploadDataframeOnTaskTask(TestCase):
    """Tests for the upload_dataframe_to_ontask_task task."""

    def setUp(self) -> None:
        self.course_id = "course-v1:edX+DemoX+Demo_Course"
        self.workflow_id = 1
        self.api_auth_token = "test-api-auth-token"

    @override_settings(ONTASK_INTERNAL_API="http://ontask:8080")
    @patch(f"{TASKS_MODULE_PATH}.get_data_summary_class")
    @patch(f"{TASKS_MODULE_PATH}.requests.put")
    @patch(f"{TASKS_MODULE_PATH}.log")
    def test_upload_dataframe_to_ontask(self, mock_log: Mock, mock_put: Mock, mock_get_data_summary_class: Mock):
        """Test uploading a dataframe to OnTask."""
        mock_data_summary_instance = Mock()
        mock_data_summary_instance.get_data_summary.return_value = {"data": "frame"}
        mock_get_data_summary_class.return_value = Mock(return_value=mock_data_summary_instance)
        mock_put.return_value = Mock(status_code=status.HTTP_200_OK)

        upload_dataframe_to_ontask_task(self.course_id, self.workflow_id, self.api_auth_token)

        mock_put.assert_called_once_with(
            url=f"{settings.ONTASK_INTERNAL_API}/table/{self.workflow_id}/ops/",
            json={"data_frame": {"data": "frame"}},
            headers={"Authorization": f"Token {self.api_auth_token}"},
            timeout=5,
        )
        mock_log.info.assert_called_with("Put request to OnTask: 200")
