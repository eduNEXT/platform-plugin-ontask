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
    UNIQUE_KEY_LENGTH = 5
    COMPONENT_NAME_LENGTH = 20
    UNIT_NAME_LENGTH = 16

    def get_component_name(self, block_id, component_name, unit_blockid, unit_name) -> str:
        """
        Returns a string with a mix of the original location values.

        Returns:
            str: A formatted string with the shortened values.
        """

        def shorten(value, length):
            """Shorten the string to the specified length."""
            return value[:length-5] + '..' + value[-3:] if len(value) > length else value

        short_block_id = block_id[-self.UNIQUE_KEY_LENGTH:]
        short_component_name = shorten(component_name, self.COMPONENT_NAME_LENGTH)
        short_unit_blockid = unit_blockid[-self.UNIQUE_KEY_LENGTH:]
        short_unit_name = shorten(unit_name, self.UNIT_NAME_LENGTH)

        return f"{short_unit_name}({short_unit_blockid})> {short_component_name} {short_block_id} Grade"

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
            data_frame[self.USER_ID_COLUMN_NAME][index] = user_id
            for component, unit_blockid, unit_name in course_components:
                usage_key = component.usage_key
                student_module = get_score(user_id, usage_key)
                grade = student_module.grade if student_module and student_module.grade is not None else 0

                column_name = self.get_component_name(
                    component.usage_key.block_id,
                    component.display_name_with_default,
                    unit_blockid,
                    unit_name,
                )
                data_frame[column_name][index] = grade

        return data_frame
