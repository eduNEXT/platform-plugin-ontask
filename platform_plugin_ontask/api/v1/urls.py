"""URL patterns for the OnTask plugin."""

from django.urls import path

from platform_plugin_ontask.api.v1 import views

app_name = "platform_plugin_ontask"

urlpatterns = [
    path("workflow/", views.OnTaskWorkflowAPIView.as_view(), name="workflow"),
    path("table/", views.OnTaskTableAPIView.as_view(), name="table"),
]
