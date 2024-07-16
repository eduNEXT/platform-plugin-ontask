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
        Iterable: List of units.
    """
    course = modulestore().get_course(course_key, depth=0)
    for section in course.get_children():
        for subsection in section.get_children():
            yield from subsection.get_children()


def _(text):
    """
    Make '_' a no-op so we can scrape strings.
    """
    return text
