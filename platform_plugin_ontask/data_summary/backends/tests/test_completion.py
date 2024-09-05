"""Tests for the Completion backend module."""

from unittest import TestCase
from unittest.mock import Mock, patch

from platform_plugin_ontask.data_summary.backends.completion import UnitCompletionDataSummary


class TestUnitCompletionDataSummary(TestCase):
    """Tests for the Unit Completion data summary class."""

    def setUp(self):
        self.course_id = "course-v1:edunext+ontask+demo"
        self.user = Mock(id=1, email="john@doe.com", username="john_doe")
        self.enrollment = Mock(user=self.user)
        self.block_id = "9c56d"
        self.unit = Mock(usage_key=Mock(block_id=self.block_id), display_name_with_default="Unit 1")

    @patch("platform_plugin_ontask.data_summary.backends.completion.get_user_enrollments")
    @patch("platform_plugin_ontask.data_summary.backends.completion.get_course_units")
    @patch("platform_plugin_ontask.data_summary.backends.completion.CompletionService")
    def test_get_data_summary(
        self, mock_completion_service: Mock, mock_get_course_units: Mock, mock_get_user_enrollments: Mock
    ):
        mock_get_user_enrollments.return_value = [self.enrollment]
        mock_get_course_units.return_value = [(self.unit, "fake_subsection_name", "fake_section_name")]
        mock_completion_service = mock_completion_service.return_value
        mock_completion_service.vertical_is_complete.return_value = True

        completion_data_summary = UnitCompletionDataSummary(self.course_id)
        result = completion_data_summary.get_data_summary()

        self.assertEqual(result["user_id"][0], self.user.id)
        self.assertIn(self.block_id, list(result.keys())[1])
        self.assertIn(self.unit.display_name_with_default, list(result.keys())[1])
        self.assertTrue(result[f"fake_se..ame> fake_su..ame> Unit 1 {self.block_id} Completed"][0])
