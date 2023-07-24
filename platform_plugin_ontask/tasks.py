"""Module for creating Celery tasks."""
import logging
from celery import shared_task
from collections import defaultdict
from django.conf import settings

from platform_plugin_ontask.utilities import (
    precompute_data_frame_columns,
    prepare_data_frame,
    get_workflow_data_frame,
    update_workflow_data_frame,
)

MAX_RETRIES = 3
DATA_FRAME_COLUMNS = precompute_data_frame_columns()
log = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=MAX_RETRIES)
def send_student_data_to_ontask(self, queues, course_id, workflow_id, **kwargs):
    """
    Send the data to the OnTask Learning installation.

    Args:
        batch (Queue): The batch of events to send. # TODO: pass thread safe queue to send
        course_id (str): The course ID where the events were generated.
        workflow_id (str): The workflow ID to send the data for.
    """
    log.info("Sending batch of {} events to OnTask Learning".format(len(queues)))
    log.info("Sending events to OnTask Learning: {}".format(queues))
    current_data_frame = get_workflow_data_frame(workflow_id)

    log.info("Current data frame in OnTask Learning: {}".format(current_data_frame))
    new_data_frame = prepare_data_frame(
        current_data_frame,
        course_id,
        queues,
        DATA_FRAME_COLUMNS,
    )

    log.info("Sending data frame to OnTask Learning: {}".format(new_data_frame))
    update_workflow_data_frame(workflow_id, new_data_frame)
