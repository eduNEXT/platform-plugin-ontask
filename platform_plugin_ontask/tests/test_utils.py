"""This module contains tests for the utility functions in the OnTask plugin."""

from unittest import TestCase
from unittest.mock import Mock

from django.test.utils import override_settings

from platform_plugin_ontask.api.utils import get_api_auth_token, get_data_summary_class
from platform_plugin_ontask.data_summary.backends.tests.dummy import DummyDataSummary
from platform_plugin_ontask.exceptions import APIAuthTokenNotSetError

DUMMY_DATA_SUMMARY_CLASS = "platform_plugin_ontask.data_summary.backends.tests.dummy.DummyDataSummary"


class TestUtils(TestCase):
    """Tests for the utility functions in the OnTask plugin."""

    def test_custom_class_found(self):
        """Test that the custom class is found and returned.

        Expected result: The custom class is found and returned.
        """
        result = get_data_summary_class(DUMMY_DATA_SUMMARY_CLASS)
        self.assertIs(result, DummyDataSummary)

    def test_custom_class_not_found(self):
        """Test that the custom class is not found.

        Expected result: None is returned.
        """
        result = get_data_summary_class("non.existent.path")
        self.assertIsNone(result)

    def test_get_api_auth_token_from_django_setting(self):
        """Test that the API auth token is generated.

        Expected result: The API auth token is generated and has a length of 40 characters.
        """
        course_block = Mock(other_course_settings={})

        token = get_api_auth_token(course_block)
        self.assertIsNotNone(token)
        self.assertEqual(token, "ontask-api-auth-token")

    @override_settings(ONTASK_API_AUTH_TOKEN=None)
    def test_get_api_auth_token_from_other_course_settings(self):
        """Test that the API auth token is generated.

        Expected result: The API auth token is generated and has a length of 40 characters.
        """
        api_auth_token = "ontask-api-auth-token-from-other-course-settings"
        course_block = Mock(other_course_settings={"ONTASK_API_AUTH_TOKEN": api_auth_token})

        token = get_api_auth_token(course_block)
        self.assertIsNotNone(token)
        self.assertEqual(token, api_auth_token)

    @override_settings(ONTASK_API_AUTH_TOKEN=None)
    def test_get_api_auth_token_not_set(self):
        """Test that the API auth token is not set.

        Expected result: APIAuthTokenNotSetError is raised.
        """
        course_block = Mock(other_course_settings={})

        with self.assertRaises(APIAuthTokenNotSetError):
            get_api_auth_token(course_block)
