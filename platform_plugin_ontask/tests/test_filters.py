"""Test suite for the filters module.

Classes:
    TestAddInstructorOnTaskTab: Test cases for the filters defined in extensions/filters.py
"""

from unittest.mock import Mock

from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings

from platform_plugin_ontask.extensions.filters import AddInstructorOnTaskTab


class TestAddInstructorOnTaskTab(TestCase):
    """Test cases for the AddInstructorOnTaskTab filter."""

    def setUp(self) -> None:
        self.filter = AddInstructorOnTaskTab(
            filter_type="instructor_dashboard",
            running_pipeline=Mock(),
        )
        self.course_id = "course-v1:edX+DemoX+Demo_Course"
        self.course = Mock(id=self.course_id, other_course_settings={"ONTASK_WORKFLOW_ID": 1})

    @override_settings(ONTASK_URL="http://localhost:8080")
    def test_run_filter(self):
        """Test the run_filter method.

        The run_filter method should add a new section to the instructor dashboard.

        The new section should have the following properties:
            - section_key: "ontask"
            - section_display_name: "OnTask"
            - template_path_prefix: "/instructor_dashboard/"
            - course_id: the course id
            - fragment: a Fragment object

        The context should also contain the following properties:

            - course_id: The course id
            - ontask_url: the ONTASK_URL setting
            - workflow_id: The ONTASK_WORKFLOW_ID setting from the course's other_course_settings
        """
        context = {"course": self.course, "sections": []}
        template_name = "instructor_dashboard.html"

        result = self.filter.run_filter(context, template_name)

        result_context = result["context"]
        first_section = result_context["sections"][0]
        self.assertEqual(len(result_context["sections"]), 1)
        self.assertEqual(result_context["ontask_url"], settings.ONTASK_URL)
        self.assertEqual(result_context["workflow_id"], self.course.other_course_settings["ONTASK_WORKFLOW_ID"])
        self.assertEqual(result_context["course_id"], self.course.id)
        self.assertEqual(first_section["section_key"], "ontask")
        self.assertEqual(first_section["section_display_name"], "OnTask")
        self.assertEqual(first_section["template_path_prefix"], "/instructor_dashboard/")
        self.assertEqual(first_section["course_id"], self.course.id)

    @override_settings(ONTASK_URL="http://localhost:8080")
    def test_run_filter_no_workflow_id(self):
        """
        Test the run_filter method when the course does not have an ONTASK_WORKFLOW_ID setting.
        """
        self.course = Mock(id=self.course_id, other_course_settings={})
        context = {"course": self.course, "sections": []}
        template_name = "instructor_dashboard.html"

        result = self.filter.run_filter(context, template_name)

        result_context = result["context"]
        self.assertIsNone(result_context["workflow_id"])
