"""Utility functions for the OnTask plugin."""

from typing import Iterable

from opaque_keys.edx.keys import CourseKey

from platform_plugin_ontask.edxapp_wrapper.modulestore import modulestore


def get_course_units(course_key: CourseKey) -> Iterable:
    """
    Extract a list of 'units' (verticals) from a course.

    Args:
        course_key (CourseKey): Course key.

    Returns:
        Iterable: List of tuples containing the unit and
        the name of its parents.
    """
    course = modulestore().get_course(course_key, depth=0)
    for section in course.get_children():
        for subsection in section.get_children():
            for unit in subsection.get_children():
                yield (
                    unit,
                    subsection.display_name_with_default,
                    section.display_name_with_default,
                )


def get_course_components(course_key: CourseKey) -> Iterable:
    """
    Extract a list of 'components' (blocks) from a course.

    Args:
        course_key (CourseKey): Course key.

    Returns:
        Iterable: List of components.
    """
    course_units_with_parent_names = get_course_units(course_key)
    for unit, subsection_name, section_name in course_units_with_parent_names:
        for component in unit.get_children():
            yield (
                component,
                unit.usage_key.block_id,
                unit.display_name_with_default,
            )


def _(text):
    """
    Make '_' a no-op so we can scrape strings.
    """
    return text
