"""Tests for the CompletionDataSummary class."""

from unittest import TestCase
from unittest.mock import Mock, patch

from platform_plugin_ontask.data_summary.backends.completion import CompletionDataSummary


class TestCompletionDataSummary(TestCase):
    """Tests for the `CompletionDataSummary` class."""

    def setUp(self):
        self.course_id = "course-v1:edunext+ontask+demo"
        self.user = Mock()
        self.user.id = 1
        self.user.email = "john@doe.com"
        self.user.username = "john_doe"
        self.enrollment = Mock(user=self.user)
        self.block_id = "9c56d"
        self.unit = Mock()
        self.unit.usage_key.block_id = self.block_id
        self.unit.display_name = "Unit 1"

    @patch("platform_plugin_ontask.data_summary.backends.completion.get_user_enrollments")
    @patch("platform_plugin_ontask.data_summary.backends.completion.get_course_units")
    @patch("platform_plugin_ontask.data_summary.backends.completion.CompletionService")
    def test_get_data_summary(
        self, MockCompletionService: Mock, mock_get_course_units: Mock, mock_get_user_enrollments: Mock
    ):
        mock_get_user_enrollments.return_value.filter.return_value = [self.enrollment]
        mock_get_course_units.return_value = [self.unit]
        mock_completion_service = MockCompletionService.return_value
        mock_completion_service.vertical_is_complete.return_value = True

        completion_data_summary = CompletionDataSummary(self.course_id)
        result = completion_data_summary.get_data_summary()

        self.assertEqual(result["user_id"][0], self.user.id)
        self.assertEqual(result["email"][0], self.user.email)
        self.assertEqual(result["username"][0], self.user.username)
        self.assertEqual(result["course_id"][0], self.course_id)
        self.assertEqual(result[f"block_id_{self.block_id}_unit_name"][0], self.unit.display_name)
        self.assertTrue(result[f"block_id_{self.block_id}_completed"][0])
