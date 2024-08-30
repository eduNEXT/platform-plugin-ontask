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
        "Section 1> Subsect..1.1> Unit 1.1.2 92909 Completed": {
            "0": False,
            "1": True,
        },
        "Section 3> Subsect..3.1> Unit 3.1.1 8c8e7 Completed": {
            "0": False,
            "1": True,
        }
    }

    ```
    """
    UNIQUE_KEY_LENGTH = 5
    UNIT_NAME_LENGTH = 16
    SUBSECTION_NAME_LENGTH = 12
    SECTION_NAME_LENGTH = 12

    def get_unit_name(self, block_id, unit_name, subsection_name, section_name) -> str:
        """
        Returns a string with a mix of the original location values.

        Args:
            block_id (str): The block ID.
            unit_name (str): The unit name.
            subsection_name (str): The subsection name.
            section_name (str): The section name.

        Returns:
            str: A formatted string with the shortened values.
        """

        def shorten(value, length):
            """Shorten the string to the specified length."""
            return value[:length-5] + '..' + value[-3:] if len(value) > length else value

        short_block_id = block_id[-self.UNIQUE_KEY_LENGTH:]
        short_unit_name = shorten(unit_name, self.UNIT_NAME_LENGTH)
        short_subsection_name = shorten(subsection_name, self.SUBSECTION_NAME_LENGTH)
        short_section_name = shorten(section_name, self.SECTION_NAME_LENGTH)

        return f"{short_section_name}> {short_subsection_name}> {short_unit_name} {short_block_id} Completed"


    def get_data_summary(self) -> dict:
        """
        Get the unit completion data summary.

        Returns:
            data_frame (dict): A dataframe with the unit completion data summary
        """
        course_key = CourseKey.from_string(self.course_id)
        enrollments = get_user_enrollments(self.course_id)
        course_units = list(get_course_units(course_key))

        data_frame = defaultdict(dict)
        for index, enrollment in enumerate(enrollments):
            completion_service = CompletionService(enrollment.user, course_key)
            data_frame[self.USER_ID_COLUMN_NAME][index] = enrollment.user.id
            for unit, subsection_name, section_name in course_units:
                column_name = self.get_unit_name(
                    unit.usage_key.block_id,
                    unit.display_name_with_default,
                    subsection_name,
                    section_name,
                )
                data_frame[column_name][index] = (
                    completion_service.vertical_is_complete(unit)
                )

        return data_frame
