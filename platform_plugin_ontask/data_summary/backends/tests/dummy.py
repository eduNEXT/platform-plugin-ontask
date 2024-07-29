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
            "id": {"0": 1},
            "user_id": {"0": 1},
            "email": {"0": "john@doe.com"},
            "username": {"0": "john_doe"},
            "course_id": {"0": "course-v1:edX+DemoX+Demo_Course"},
            "block_id": {"0": "5c56dbeb30504c8fb899553f080cf15d"},
            "block_name": {"0": "Unit 1"},
            "completed": {"0": False},
        }
        return data_frame
