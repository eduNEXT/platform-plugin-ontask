"""Test suite for the filters module.

Classes:
    TestInstructorFilters: test cases for the filters defined in extensions/filters.py
"""
from unittest.mock import Mock

from django.conf import settings
from django.test import TestCase

from platform_plugin_ontask.extensions.filters import AddInstructorLimesurveyTab


class TestAddInstructorLimesurveyTab(TestCase):
    """Test cases for the AddInstructorLimesurveyTab filter."""

    def test_run_filter(self):
        """Test the run_filter method.

        The run_filter method should add a new section to the instructor dashboard.

        The new section should have the following properties:
            - section_key: "ontask"
            - section_display_name: "On Task"
            - template_path_prefix: "/instructor_dashboard/"
            - course_id: the course id
            - fragment: a Fragment object

        The context should also contain the following properties:

            - ONTASK_URL: the ONTASK_URL setting
        """
        mock_pipeline = Mock()
        instructor_tab = AddInstructorLimesurveyTab(
            filter_type="instructor_dashboard",
            running_pipeline=mock_pipeline,
        )
        mock_course = Mock()
        context = instructor_tab.run_filter(
            context={
                "course": mock_course,
                "sections": [],
            },
            template_name="instructor_dashboard.html",
        )
        self.assertEqual(len(context["sections"]), 1)
        self.assertEqual(context["sections"][0]["section_key"], "ontask")
        self.assertEqual(context["sections"][0]["section_display_name"], "On Task")
        self.assertEqual(
            context["sections"][0]["template_path_prefix"], "/instructor_dashboard/"
        )
        self.assertEqual(context["sections"][0]["course_id"], str(mock_course.id))
        self.assertIn("ONTASK_URL", context)
        self.assertEqual(context["ONTASK_URL"], settings.ONTASK_URL)
