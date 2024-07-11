"""Tests for the tasks module of the OnTask plugin."""

from unittest import TestCase
from unittest.mock import Mock, patch

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
    @patch(f"{TASKS_MODULE_PATH}.OnTaskClient.update_table")
    @patch(f"{TASKS_MODULE_PATH}.log")
    def test_upload_dataframe_to_ontask(
        self, mock_log: Mock, mock_update_table: Mock, mock_get_data_summary_class: Mock
    ):
        """Test uploading a dataframe to OnTask."""
        mock_data_summary_instance = Mock()
        mock_data_summary_instance.get_data_summary.return_value = {"data": "frame"}
        mock_get_data_summary_class.return_value = Mock(return_value=mock_data_summary_instance)
        mock_update_table.return_value = Mock(status_code=status.HTTP_200_OK, text="response", url="ontask-url")

        upload_dataframe_to_ontask_task(self.course_id, self.workflow_id, self.api_auth_token)

        mock_update_table.assert_called_once_with(self.workflow_id, {"data": "frame"})
        mock_log.info.assert_called_with(
            f"PUT {mock_update_table.return_value.url} "
            f"| status-code={status.HTTP_200_OK} "
            f"| response={mock_update_table.return_value.text}"
        )
