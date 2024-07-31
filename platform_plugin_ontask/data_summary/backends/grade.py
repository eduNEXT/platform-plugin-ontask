"""Data summary for grade data."""

from collections import defaultdict

from opaque_keys.edx.keys import CourseKey

from platform_plugin_ontask.data_summary.backends.base import DataSummary
from platform_plugin_ontask.edxapp_wrapper.courseware import get_score
from platform_plugin_ontask.edxapp_wrapper.enrollments import get_user_enrollments
from platform_plugin_ontask.utils import get_course_components


class ComponentGradeDataSummary(DataSummary):
    """
    Data summary for the grade of the components in a course.

    A component grade data summary is a summary of all the grade data of the
    components in a specific course. Each record contains the user ID and the
    grade of each component.

    `get_data_summary` performs the following steps:

    1. Get the course key from the course ID.
    2. Get all the enrollments for the course.
    3. Get all the course components for the course.
    4. Create a dictionary with the component grade data summary.

    Example result:

    ```python

    grade_data_summary = ComponentGradeDataSummary()
    grade_data_summary.get_data_summary()

    {
        "user_id": {
            "0": 5,
            "1": 6,
        },
        "component_9c56dbeb30504c8fb799553f080cf15d_grade": {
            "0": 1,
            "1": 0,
        },
        "component_6c7e4b1b7b7e4b3e8b7b7e4b3e8b7b7_grade": {
            "0": 0,
            "1": 1,
        },
        ...
    }

    ```
    """

    GRADE = "component_{}_grade"

    def get_data_summary(self) -> dict:
        """
        Get the component completion data summary.

        Returns:
            data_frame (dict): A dataframe with the component completion data summary
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
