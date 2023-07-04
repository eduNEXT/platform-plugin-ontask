"""
platform_plugin_ontask Django application initialization.
"""

from django.apps import AppConfig


class PlatformPluginOntaskConfig(AppConfig):
    """
    Configuration for the platform_plugin_ontask Django application.
    """

    name = 'platform_plugin_ontask'

    plugin_app = {
        "settings_config": {
            "lms.djangoapp": {
                "common": {"relative_path": "settings.common"},
                "test": {"relative_path": "settings.test"},
                "production": {"relative_path": "settings.production"},
            },
            "cms.djangoapp": {
                "common": {"relative_path": "settings.common"},
                "test": {"relative_path": "settings.test"},
                "production": {"relative_path": "settings.production"},
            },
        },
    }
