"""
Common Django settings for eox_hooks project.
For more information on this file, see
https://docs.djangoproject.com/en/2.22/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.22/ref/settings/
"""

from platform_plugin_ontask import ROOT_DIRECTORY

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.22/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "secret-key"


# Application definition

INSTALLED_APPS = []


# Internationalization
# https://docs.djangoproject.com/en/2.22/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_TZ = True


def plugin_settings(settings):
    """
    Set of plugin settings used by the Open Edx platform.
    More info: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    settings.MAKO_TEMPLATE_DIRS_BASE.append(ROOT_DIRECTORY / "templates")
    settings.ONTASK_URL = "http://ontask.local.overhang.io:8080/"
    settings.PLATFORM_PLUGIN_ONTASK_AUTHENTICATION_BACKEND = (
        "platform_plugin_ontask.edxapp_wrapper.backends.authentication_r_v1"
    )
    settings.PLATFORM_PLUGIN_ONTASK_MODULESTORE_BACKEND = (
        "platform_plugin_ontask.edxapp_wrapper.backends.modulestore_r_v1"
    )
    settings.PLATFORM_PLUGIN_ONTASK_ENROLLMENTS_BACKEND = (
        "platform_plugin_ontask.edxapp_wrapper.backends.enrollments_r_v1"
    )
    settings.PLATFORM_PLUGIN_ONTASK_COMPLETION_BACKEND = (
        "platform_plugin_ontask.edxapp_wrapper.backends.completion_r_v1"
    )
    settings.PLATFORM_PLUGIN_ONTASK_COURSEWARE_BACKEND = (
        "platform_plugin_ontask.edxapp_wrapper.backends.courseware_r_v1"
    )
    settings.ONTASK_DATA_SUMMARY_CLASSES = [
        "platform_plugin_ontask.data_summary.backends.user.UserDataSummary",
        "platform_plugin_ontask.data_summary.backends.completion.UnitCompletionDataSummary",
        "platform_plugin_ontask.data_summary.backends.grade.ComponentGradeDataSummary",
    ]
