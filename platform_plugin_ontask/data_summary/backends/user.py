"""Data summary for completion data."""

from collections import defaultdict

from platform_plugin_ontask.data_summary.backends.base import DataSummary
from platform_plugin_ontask.edxapp_wrapper.enrollments import get_user_enrollments


class UserDataSummary(DataSummary):
    """
    A class that provides a summary of user data for a given course to pass
    to an OnTask Workflow.

    Example result:

    ```python

    data_summary = UserDataSummary()
    data_summary.get_data_summary()

    {
        "user_id": {
            "0": 5,
            "1": 6,
        },
        "email": {
            "0": "test@example.com",
            "1": "author@courses.com",
        },
        "username": {
            "0": "test",
            "1": "author",
        },
        ...
    }

    ```
    """
    EMAIL_COLUMN_NAME = "email"
    USERNAME_COLUMN_NAME = "username"

    def get_data_summary(self) -> dict:
        """
        Get the user data summary.

        Returns:
            data_frame (dict): A dataframe with the user data summary
        """
        enrollments = get_user_enrollments(self.course_id)

        data_frame = defaultdict(dict)
        for index, enrollment in enumerate(enrollments):
            data_frame[self.USER_ID_COLUMN_NAME][index] = enrollment.user.id
            data_frame[self.EMAIL_COLUMN_NAME][index] = enrollment.user.email
            data_frame[self.USERNAME_COLUMN_NAME][index] = enrollment.user.username

        return data_frame
