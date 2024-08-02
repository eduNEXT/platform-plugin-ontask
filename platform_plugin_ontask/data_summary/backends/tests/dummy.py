"""Dummy data summary for testing purposes."""

from platform_plugin_ontask.data_summary.backends.base import DataSummary


class DummyDataSummary(DataSummary):
    """Dummy data summary for testing purposes."""

    def get_data_summary(self) -> dict:
        """
        Get a dummy data summary.

        Returns:
            dict: A dummy data summary.
        """
        data_frame = {
            "user_id": {"0": 1},
            "email": {"0": "john@doe.com"},
            "username": {"0": "john_doe"},
            "course_id": {"0": "course-v1:edX+DemoX+Demo_Course"},
            "block_id_e1d8b56763fe48fbb935f9619220ab53_dummy": {"0": True},
        }
        return data_frame
