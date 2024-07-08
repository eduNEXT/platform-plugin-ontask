"""Celery tasks for the OnTask plugin."""

from logging import getLogger

from celery import shared_task
from django.conf import settings

from platform_plugin_ontask.api.utils import get_data_summary_class
from platform_plugin_ontask.client import OnTaskClient

log = getLogger(__name__)


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

    ontask_client = OnTaskClient(settings.ONTASK_INTERNAL_API, api_auth_token)
    response = ontask_client.update_table(workflow_id, data_frame)

    log.info(f"PUT {response.url} | status-code={response.status_code} | response={response.text}")
