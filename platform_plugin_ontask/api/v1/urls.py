"""URL patterns for the OnTask plugin."""

from django.urls import path

from platform_plugin_ontask.api.v1 import views

app_name = "platform_plugin_ontask"

urlpatterns = [
    path("create-workflow/", views.OntaskWorkflowView.as_view(), name="create-workflow"),
]
