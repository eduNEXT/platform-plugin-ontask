"""URL patterns for the OnTask plugin."""

from django.urls import include, path

app_name = "platform_plugin_ontask"

urlpatterns = [
    path("v1/", include("platform_plugin_ontask.api.v1.urls", namespace="v1")),
]
