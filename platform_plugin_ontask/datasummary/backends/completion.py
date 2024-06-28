"""Data summary for completion data."""

from collections import defaultdict

from opaque_keys.edx.keys import CourseKey

from platform_plugin_ontask.datasummary.backends.base import DataSummary
from platform_plugin_ontask.edxapp_wrapper.completion import CompletionService
from platform_plugin_ontask.edxapp_wrapper.enrollments import get_user_enrollments


class CompletionDataSummary(DataSummary):
    """Data summary for completion data."""

    def get_data_summary(self) -> dict:
        """
        Get the completion data summary.

        Returns:
            dict: A dataframe with the completion data summary
        """
        # Avoid circular import
        from platform_plugin_ontask.api.utils import get_course_units  # pylint: disable=import-outside-toplevel

        course_key = CourseKey.from_string(self.course_id)
        enrollments = get_user_enrollments(self.course_id).filter(user__is_superuser=False, user__is_staff=False)
        course_units = list(get_course_units(course_key))
        data_frame = defaultdict(dict)

        index = 0
        for enrollment in enrollments:
            completion_service = CompletionService(enrollment.user, course_key)
            for unit in course_units:
                data_frame["id"][index] = index + 1
                data_frame["user_id"][index] = enrollment.user.id
                data_frame["email"][index] = enrollment.user.email
                data_frame["username"][index] = enrollment.user.username
                data_frame["course_id"][index] = self.course_id
                data_frame["block_id"][index] = unit.usage_key.block_id
                data_frame["block_name"][index] = unit.display_name
                data_frame["completed"][index] = completion_service.vertical_is_complete(unit)
                index += 1

        return data_frame
