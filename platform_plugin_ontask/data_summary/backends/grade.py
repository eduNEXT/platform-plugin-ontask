"""Data summary for grade data."""

from collections import defaultdict

from opaque_keys.edx.keys import CourseKey

from platform_plugin_ontask.data_summary.backends.base import DataSummary
from platform_plugin_ontask.edxapp_wrapper.courseware import get_score
from platform_plugin_ontask.edxapp_wrapper.enrollments import get_user_enrollments
from platform_plugin_ontask.utils import get_course_components


class ComponentsGradeDataSummary(DataSummary):
    """
    Data summary for components grade data.

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

    grade_data_summary = GradeDataSummary()
    grade_data_summary.get_data_summary()

    {
        "user_id": {
            "0": 5,
            "1": 6,
        },
        "email": {
            "0": "jhon@doe.com",
            "1": "jane@doe.com",
        },
        "component_9c56dbeb30504c8fb799553f080cf15d_grade": {
            "0": 1.0,
            "1": 0.5,
        },
    }

    ```
    """

    GRADE = "component_{}_grade"

    def get_data_summary(self) -> dict:
        """
        Get the completion data summary.

        Returns:
            dict: A dataframe with the completion data summary
        """
        course_key = CourseKey.from_string(self.course_id)
        enrollments = get_user_enrollments(self.course_id).filter(user__is_superuser=False, user__is_staff=False)
        course_components = list(get_course_components(course_key))

        data_frame = defaultdict(dict)
        for index, enrollment in enumerate(enrollments):
            user_id = enrollment.user.id
            data_frame[self.USER_ID][index] = user_id
            for component in course_components:
                usage_key = component.usage_key
                student_module = get_score(user_id, usage_key)
                grade = student_module.grade if student_module and student_module.grade is not None else 0
                data_frame[self.GRADE.format(usage_key.block_id)][index] = grade

        return data_frame
