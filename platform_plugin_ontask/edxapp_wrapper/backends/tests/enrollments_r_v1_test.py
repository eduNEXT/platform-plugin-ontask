"""
Enrollments test definitions for Open edX Redwood release.
"""

from unittest.mock import Mock


def get_user_enrollments(*args, **kwargs):
    """
    update_item test backend.
    """
    return [
        Mock(user=Mock(id=1)),
        Mock(user=Mock(id=2)),
        Mock(user=Mock(id=3)),
    ]
