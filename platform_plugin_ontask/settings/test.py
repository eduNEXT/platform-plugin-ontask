"""
These settings are here to use during tests, because django requires them.

In a real-world use case, apps in this project are installed into other
Django applications, so these settings will not be used.
"""

from os.path import abspath, dirname, join


def root(*args):
    """
    Get the absolute path of the given path relative to the project root.
    """
    return join(abspath(dirname(__file__)), *args)


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "default.db",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    }
}

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "platform_plugin_ontask",
)

LOCALE_PATHS = [
    root("platform_plugin_ontask", "conf", "locale"),
]

SECRET_KEY = "insecure-secret-key"

MIDDLEWARE = (
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": False,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",  # this is required for admin
                "django.contrib.messages.context_processors.messages",  # this is required for admin
            ],
        },
    }
]

ONTASK_URL = "http://localhost:8000"

# Settings for the OnTask plugin
PLATFORM_PLUGIN_ONTASK_AUTHENTICATION_BACKEND = (
    "platform_plugin_ontask.edxapp_wrapper.backends.tests.authentication_r_v1_test"
)
PLATFORM_PLUGIN_ONTASK_MODULESTORE_BACKEND = (
    "platform_plugin_ontask.edxapp_wrapper.backends.tests.modulestore_r_v1_test"
)
PLATFORM_PLUGIN_ONTASK_ENROLLMENTS_BACKEND = (
    "platform_plugin_ontask.edxapp_wrapper.backends.tests.enrollments_r_v1_test"
)
