"""Celery tasks for the OnTask plugin."""

from celery import shared_task

from platform_plugin_ontask.api.utils import upload_dataframe_to_ontask


@shared_task
def upload_dataframe_to_ontask_task(course_id: str, workflow_id: str, api_auth_token: str) -> None:
    """
    Task to upload a data frame to an Workflow in OnTask.

    Args:
        course_id (str): The course ID.
        workflow_id (str): The OnTask workflow ID.
        api_auth_token (str): The OnTask API authentication token.
    """
    return upload_dataframe_to_ontask(course_id, workflow_id, api_auth_token)
