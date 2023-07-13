"""Module for creating Celery tasks."""

import json
import requests

from celery import shared_task

from platform_plugin_ontask.utilities import make_request_to_ontask

MAX_RETRIES = 3


@shared_task(bind=True, max_retries=MAX_RETRIES)
def handle_events_batch(course_id, event, queues, **kwargs):
    """
    Handle what happens next when an event is emitted.

    Before adding an event to the queue:
     - It is formatted to be sent to the OnTask Learning installation.
     - The queue is checked to see if the batch size has been reached.
    If not, the event is added to the queue.
    If the batch size has been reached, the batch is sent to the OnTask Learning installation.

    Args:
        course_id (str): The current course ID.
        event (dict): The event to handle.
        queues (list): The list of queues.
    """



@shared_task(bind=True, max_retries=MAX_RETRIES)
def send_student_data_to_ontask(batch, **kwargs):
    """
    Send the data to the OnTask Learning installation.

    Args:
        batch (Queue): The batch of events to send. # TODO: pass thread safe queue to send
    """
