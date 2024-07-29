"""This module contains tests for the utility functions in the OnTask plugin."""

from unittest import TestCase

from django.test import override_settings

from platform_plugin_ontask.api.utils import get_data_summary_class
from platform_plugin_ontask.data_summary.backends.completion import CompletionDataSummary
from platform_plugin_ontask.data_summary.backends.tests.dummy import DummyDataSummary

DUMMY_DATA_SUMMARY_CLASS = "platform_plugin_ontask.datasummary.backends.tests.dummy.DummyDataSummary"


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
