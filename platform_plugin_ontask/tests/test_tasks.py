"""Tests for the tasks module of the OnTask plugin."""

from unittest import TestCase
from unittest.mock import Mock, patch

from rest_framework import status

from platform_plugin_ontask.api.utils import ontask_log_from_response
from platform_plugin_ontask.data_summary.backends.tests.dummy import DummyDataSummary
from platform_plugin_ontask.tasks import upload_dataframe_to_ontask_task

TASKS_MODULE_PATH = "platform_plugin_ontask.tasks"


class TestUploadDataframeOnTaskTask(TestCase):
    """Tests for the upload_dataframe_to_ontask_task task."""

    def setUp(self) -> None:
        self.course_id = "course-v1:edX+DemoX+Demo_Course"
        self.workflow_id = 1
        self.api_auth_token = "test-api-auth-token"

    @patch(f"{TASKS_MODULE_PATH}.OnTaskClient.merge_table")
    @patch(f"{TASKS_MODULE_PATH}.log")
    def test_upload_dataframe_to_ontask(
        self,
        mock_log: Mock,
        mock_merge_table: Mock,
    ):
        """Test uploading a dataframe to OnTask."""
        mock_merge_table.return_value = Mock(status_code=status.HTTP_200_OK, text="response", url="ontask-url")

        upload_dataframe_to_ontask_task(self.course_id, self.workflow_id, self.api_auth_token)

        mock_merge_table.assert_called_once_with(self.workflow_id, DummyDataSummary(self.course_id).get_data_summary())
        mock_log.info.assert_called_with(ontask_log_from_response(mock_merge_table.return_value))
