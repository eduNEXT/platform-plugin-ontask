"""Tests for the Grade Backend module."""

from unittest import TestCase
from unittest.mock import Mock, patch

from platform_plugin_ontask.data_summary.backends.grade import ComponentGradeDataSummary


class TestComponentGradeDataSummary(TestCase):
    """Tests for the Component Grade data summary class."""

    def setUp(self):
        self.course_id = "course-v1:edunext+ontask+demo"
        self.user = Mock(id=1, email="john@doe.com", username="john_doe")
        self.enrollment = Mock(user=self.user)
        self.block_id = "6b7e4"
        self.component = Mock(usage_key=Mock(block_id=self.block_id), display_name_with_default="fake_component_name")

    @patch("platform_plugin_ontask.data_summary.backends.grade.get_user_enrollments")
    @patch("platform_plugin_ontask.data_summary.backends.grade.get_course_components")
    @patch("platform_plugin_ontask.data_summary.backends.grade.get_score")
    def test_get_data_summary(
        self, mock_get_score: Mock, mock_get_course_components: Mock, mock_get_user_enrollments: Mock
    ):
        mock_get_score.return_value = Mock(grade=1)
        mock_get_user_enrollments.return_value = [self.enrollment]
        mock_get_course_components.return_value = [(self.component, "fake_unit_blockid", "fake_unit_name")]

        grade_data_summary = ComponentGradeDataSummary(self.course_id)
        result = grade_data_summary.get_data_summary()

        self.assertEqual(result["user_id"][0], self.user.id)
        self.assertIn("fake_unit_name", list(result.keys())[1])
        self.assertIn("fake_component_name", list(result.keys())[1])
