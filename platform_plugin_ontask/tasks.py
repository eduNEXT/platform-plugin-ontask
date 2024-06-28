"""Celery tasks for the OnTask plugin."""

import requests
from celery import shared_task
from django.conf import settings

from platform_plugin_ontask.api.utils import get_data_summary_class


@shared_task
def upload_dataframe_to_ontask_task(course_id: str, workflow_id: str, api_auth_token: str) -> None:
    """
    Task to upload a dataframe to a OnTask workflow.

    Args:
        course_id (str): The course ID.
        workflow_id (str): The OnTask workflow ID.
        api_auth_token (str): The OnTask API authentication token.
    """
    data_summary_class = get_data_summary_class()
    data_summary_instance = data_summary_class(course_id)
    data_frame = data_summary_instance.get_data_summary()

    requests.put(
        url=f"{settings.ONTASK_INTERNAL_API}/table/{workflow_id}/ops/",
        json={"data_frame": data_frame},
        headers={"Authorization": f"Token {api_auth_token}"},
        timeout=5,
    )
