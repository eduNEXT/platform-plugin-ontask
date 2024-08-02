"""Celery tasks for the OnTask plugin."""

import logging

from celery import shared_task
from django.conf import settings

from platform_plugin_ontask.api.utils import get_data_summary_class
from platform_plugin_ontask.client import OnTaskClient

log = logging.getLogger(__name__)


@shared_task
def upload_dataframe_to_ontask_task(course_id: str, workflow_id: str, api_auth_token: str) -> None:
    """
    Task to upload a dataframe to a OnTask workflow.

    If the `ONTASK_DATA_SUMMARY_CLASSES` setting is not set, the task will log an
    error message and return.

    For each data summary class in the `ONTASK_DATA_SUMMARY_CLASSES` setting, the
    task will create an instance of the class and call the `get_data_summary` method
    to get the dataframe. The task will then merge the dataframe to the current
    OnTask table.

    Args:
        course_id (str): The course ID.
        workflow_id (str): The OnTask workflow ID.
        api_auth_token (str): The OnTask API authentication token.
    """
    data_summary_classes = getattr(settings, "ONTASK_DATA_SUMMARY_CLASSES", [])

    if not data_summary_classes:
        log.info("ONTASK_DATA_SUMMARY_CLASSES is not set.")

    ontask_client = OnTaskClient(settings.ONTASK_INTERNAL_API, api_auth_token)
    for data_summary_class_path in data_summary_classes:
        data_summary_class = get_data_summary_class(data_summary_class_path)
        if data_summary_class is None:
            log.error(f"Data summary class {data_summary_class_path} not found.")
            continue

        data_summary_instance = data_summary_class(course_id)
        data_frame = data_summary_instance.get_data_summary()

        response = ontask_client.merge_table(workflow_id, data_frame)

        log.info(response.text)
