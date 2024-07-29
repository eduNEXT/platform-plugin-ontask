"""This module contains tests for the utility functions in the OnTask plugin."""

from unittest import TestCase

from platform_plugin_ontask.api.utils import get_data_summary_class
from platform_plugin_ontask.data_summary.backends.tests.dummy import DummyDataSummary

DUMMY_DATA_SUMMARY_CLASS = "platform_plugin_ontask.data_summary.backends.tests.dummy.DummyDataSummary"


class TestUtils(TestCase):
    """Tests for the utility functions in the OnTask plugin."""

    def test_custom_class_found(self):
        result = get_data_summary_class(DUMMY_DATA_SUMMARY_CLASS)
        self.assertIs(result, DummyDataSummary)

    def test_custom_class_not_found(self):
        result = get_data_summary_class("non.existent.path")
        self.assertIsNone(result)
