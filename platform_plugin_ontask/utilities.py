"""
Utilities for the OnTask Learning platform plugin.
"""
import json
import requests

from django.conf import settings

ONTASK_REQUEST_HEADERS = {
    "Content-Type": "application/json",
}


def make_request_to_ontask(request_type, path, data={}, **kwargs):
    """
    Make a request to the OnTask Learning installation.

    Args:
        request_type (requests.request): The type of request to make.
        path (str): The path to make the request to.
        data (dict): The data to send with the request.
    """
    serialized_data = json.dumps(data)
    auth_token = getattr(settings, "ONTASK_AUTH_TOKEN", None)

    response = request_type(
        f"{settings.ONTASK_SERVICE_URL}/{path}",
        data=serialized_data,
        headers={
            "Authorization": f"Token {auth_token}",
            **ONTASK_REQUEST_HEADERS,
        },
    )
    print("Response from OnTask Learning: {}".format(response))

    if 200 <= response.status_code < 300:
        return response.json()

    print("Error making request to OnTask Learning: {}".format(response))


def get_workflow_data_frame(workflow_id, **kwargs):
    """
    Get the data frame for the workflow in OnTask Learning.

    Args:
        workflow_id (str): The ID of the workflow to get the data frame for.
    """
    return make_request_to_ontask(
        requests.get,
        f"table/{workflow_id}/ops/",
    )


def update_workflow_data_frame(workflow_id, data_frame, **kwargs):
    """
    Update the data frame for the workflow in OnTask Learning.

    Args:
        workflow_id (str): The ID of the workflow to update the data frame for.
        data_frame (dict): The data frame to update the workflow with.
    """
    return make_request_to_ontask(
        requests.put,
        f"table/{workflow_id}/ops/",
        data=data_frame,
    )


def precompute_data_frame_columns():
    """
    Precompute the columns for the data frame in runtime.
    """
    ontask_xapi_events = getattr(settings, "ONTASK_XAPI_EVENTS", {})

    columns = ["name"]

    for _, event_data in ontask_xapi_events.items():
        columns.extend(event_data["context"])
        columns.extend(event_data["event"])

    return list(set(columns))


def prepare_data_frame(data_frame, course_id, queue, data_frame_columns):
    """
    Prepare the data frame to be sent to OnTask Learning.

    Args:
        data_frame (dict): The existent workflow data frame from OnTask if any.
        course_id (str): The course ID to prepare the data frame for.
        queue (dict): The queue of events to prepare the data frame for.
        data_frame_columns (list): The columns to include in the data frame.
    """
    if not data_frame["data_frame"]:
        data_frame = {
            "data_frame": {
                key: {} for key in data_frame_columns
            },
        }

    batch_start = len(data_frame["data_frame"]["name"])
    current_batch = queue[course_id]

    for index, event in enumerate(current_batch, start=batch_start):
        for key in data_frame_columns:
            data_frame["data_frame"][key][str(index)] = event.get(key)

    return data_frame
