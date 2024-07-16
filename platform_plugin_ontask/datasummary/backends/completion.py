"""Data summary for completion data."""

from collections import defaultdict

from opaque_keys.edx.keys import CourseKey

from platform_plugin_ontask.datasummary.backends.base import DataSummary
from platform_plugin_ontask.edxapp_wrapper.completion import CompletionService
from platform_plugin_ontask.edxapp_wrapper.enrollments import get_user_enrollments
from platform_plugin_ontask.utils import get_course_units


class CompletionDataSummary(DataSummary):
    """
    Data summary for completion data.

    A completion data summary is a summary of all the completion data for a specific course.
    Each record contains information about the user, the course, the unit, and whether the
    user has completed the unit.

    `get_data_summary` performs the following steps:

    1. Get the course key from the course ID.
    2. Get all the enrollments for the course.
    3. Get all the course units for the course.
    4. Create a dictionary with the completion data summary.

    Example result:

    ```python

    completion_data_summary = CompletionDataSummary()
    completion_data_summary.get_data_summary()

    {
        "id": {
            "0": 1,
            "1": 2,
        },
        "user_id": {
            "0": 5,
            "1": 6,
        },
        "email": {
            "0": "jhon@doe.com",
            "1": "jane@doe.com",
        },
        "username": {
            "0": "john",
            "1": "jane",
        },
        "course_id": {
            "0": "course-v1:edunext+ontask+demo",
            "1": "course-v1:edunext+ontask+demo",
        },
        "block_id": {
            "0": "9c56dbeb30504c8fb799553f080cf15d",
            "1": "9c56dbeb30504c8fb799553f080cf15d",
        },
        "block_name": {
            "0": "Unit 1.1",
            "1": "Unit 1.1",
        },
        "completed": {
            "0": False,
            "1": True,
        }
    }
    ```
    """

    ID = "id"
    USER_ID = "user_id"
    EMAIL = "email"
    USERNAME = "username"
    COURSE_ID = "course_id"
    UNIT_ID = "unit_id"
    UNIT_NAME = "unit_name"
    COMPLETED = "completed"

    def get_data_summary(self) -> dict:
        """
        Get the completion data summary.

        Returns:
            dict: A dataframe with the completion data summary
        """
        course_key = CourseKey.from_string(self.course_id)
        enrollments = get_user_enrollments(self.course_id).filter(user__is_superuser=False, user__is_staff=False)
        course_units = list(get_course_units(course_key))

        data_frame = defaultdict(dict)
        unique_id = 0
        for enrollment in enrollments:
            completion_service = CompletionService(enrollment.user, course_key)
            for unit in course_units:
                data_frame[self.ID][unique_id] = unique_id + 1
                data_frame[self.USER_ID][unique_id] = enrollment.user.id
                data_frame[self.EMAIL][unique_id] = enrollment.user.email
                data_frame[self.USERNAME][unique_id] = enrollment.user.username
                data_frame[self.COURSE_ID][unique_id] = self.course_id
                data_frame[self.UNIT_ID][unique_id] = unit.usage_key.block_id
                data_frame[self.UNIT_NAME][unique_id] = unit.display_name
                data_frame[self.COMPLETED][unique_id] = completion_service.vertical_is_complete(unit)
                unique_id += 1

        return data_frame
