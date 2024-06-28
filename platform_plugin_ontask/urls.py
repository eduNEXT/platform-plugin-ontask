"""URL patterns for the OnTask plugin."""

from django.urls import include, path

app_name = "platform_plugin_ontask"

urlpatterns = [
    path("api/", include("platform_plugin_ontask.api.urls", namespace="ontask-plugin-api")),
]
