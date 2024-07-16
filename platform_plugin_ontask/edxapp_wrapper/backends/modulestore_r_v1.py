"""
Modulestore definitions for Open edX Redwood release.
"""

# pylint: disable=import-error
from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.django import modulestore


def update_item(course_key, course_block, user_id):
    """
    update_item backend.

    Updates both the draft and published branches.
    """
    with modulestore().bulk_operations(course_key):
        with modulestore().branch_setting(ModuleStoreEnum.Branch.draft_preferred):
            modulestore().update_item(course_block, user_id)
        return modulestore().update_item(course_block, user_id)
