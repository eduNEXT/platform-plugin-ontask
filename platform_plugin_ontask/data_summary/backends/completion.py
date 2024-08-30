"""Data summary for completion data."""

from collections import defaultdict

from opaque_keys.edx.keys import CourseKey

from platform_plugin_ontask.data_summary.backends.base import DataSummary
from platform_plugin_ontask.edxapp_wrapper.completion import CompletionService
from platform_plugin_ontask.edxapp_wrapper.enrollments import get_user_enrollments
from platform_plugin_ontask.utils import get_course_units


class UnitCompletionDataSummary(DataSummary):
    """
    Data summary for the completion of the units in a course.

    A unit completion data summary is a summary of all the completion data of
    the units in a specific course. Each record contains information about the
    user, the course, the unit, and whether the user has completed the unit.

    `get_data_summary` performs the following steps:

    1. Get the course key from the course ID.
    2. Get all the enrollments for the course.
    3. Get all the course units for the course.
    4. Create a dictionary with the unit completion data summary.

    Example result:

    ```python

    completion_data_summary = UnitCompletionDataSummary()
    completion_data_summary.get_data_summary()

    {
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
        "unit_9c56dbeb30504c8fb799553f080cf15d_name": {
            "0": "Unit 1.1",
            "1": "Unit 1.1",
        },
        "unit_9c56dbeb30504c8fb799553f080cf15d_completed": {
            "0": False,
            "1": True,
        }
    }

    ```
    """
    UNIT_NAME_COLUMN_NAME = "unit_{}_name"
    COMPLETED_COLUMN_NAME = "unit_{}_completed"

    def get_data_summary(self) -> dict:
        """
        Get the unit completion data summary.

        Returns:
            data_frame (dict): A dataframe with the unit completion data summary
        """
        course_key = CourseKey.from_string(self.course_id)
        enrollments = get_user_enrollments(self.course_id).filter(user__is_superuser=False, user__is_staff=False)
        course_units = list(get_course_units(course_key))

        data_frame = defaultdict(dict)
        for index, enrollment in enumerate(enrollments):
            completion_service = CompletionService(enrollment.user, course_key)
            data_frame[self.USER_ID_COLUMN_NAME][index] = enrollment.user.id
            for unit in course_units:
                block_id = unit.usage_key.block_id
                data_frame[self.UNIT_NAME_COLUMN_NAME.format(block_id)][index] = unit.display_name
                data_frame[self.COMPLETED_COLUMN_NAME.format(block_id)][index] = (
                    completion_service.vertical_is_complete(unit)
                )

        return data_frame
