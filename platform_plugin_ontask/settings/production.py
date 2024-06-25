"""
Production Django settings for eox_hooks project.
"""


def plugin_settings(settings):
    """
    Set of plugin settings used by the Open Edx platform.
    More info: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    settings.ONTASK_URL = getattr(settings, "ENV_TOKENS", {}).get("ONTASK_URL", settings.ONTASK_URL)
    settings.PLATFORM_PLUGIN_ONTASK_AUTHENTICATION_BACKEND = getattr(settings, "ENV_TOKENS", {}).get(
        "PLATFORM_PLUGIN_ONTASK_AUTHENTICATION_BACKEND", settings.PLATFORM_PLUGIN_ONTASK_AUTHENTICATION_BACKEND
    )
    settings.PLATFORM_PLUGIN_ONTASK_MODULESTORE_BACKEND = getattr(settings, "ENV_TOKENS", {}).get(
        "PLATFORM_PLUGIN_ONTASK_MODULESTORE_BACKEND", settings.PLATFORM_PLUGIN_ONTASK_MODULESTORE_BACKEND
    )
