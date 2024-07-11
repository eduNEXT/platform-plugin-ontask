"""This module contains tests for the utility functions in the OnTask plugin."""

from unittest import TestCase

from ddt import data, ddt, unpack
from django.test import override_settings
from rest_framework import status

from platform_plugin_ontask.api.utils import api_error, get_data_summary_class
from platform_plugin_ontask.datasummary.backends.completion import CompletionDataSummary
from platform_plugin_ontask.datasummary.backends.tests.dummy import DummyDataSummary

DUMMY_DATA_SUMMARY_CLASS = "platform_plugin_ontask.datasummary.backends.tests.dummy.DummyDataSummary"


@ddt
class TestUtils(TestCase):
    """Tests for the utility functions in the OnTask plugin."""

    @override_settings(ONTASK_DATA_SUMMARY_CLASS=None)
    def test_default_class_return(self):
        result = get_data_summary_class()
        self.assertIs(result, CompletionDataSummary)

    @override_settings(ONTASK_DATA_SUMMARY_CLASS=DUMMY_DATA_SUMMARY_CLASS)
    def test_custom_class_return(self):
        result = get_data_summary_class()
        self.assertIs(result, DummyDataSummary)

    @data(
        ("Custom field error message", status.HTTP_400_BAD_REQUEST),
        ("Another custom field error message", status.HTTP_404_NOT_FOUND),
        ("Yet another custom field error message", status.HTTP_500_INTERNAL_SERVER_ERROR),
        ({"error": "Custom field error message"}, status.HTTP_400_BAD_REQUEST),
    )
    @unpack
    def test_api_error(self, error: str, status_code: int):
        response = api_error(error, status_code)

        self.assertEqual(response.status_code, status_code)
        self.assertDictEqual(response.data, {"error": error})
