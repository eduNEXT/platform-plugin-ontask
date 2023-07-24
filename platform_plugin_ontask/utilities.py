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
        return response

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

    The columns are computed based on the ONTASK_XAPI_EVENTS setting. The setting looks like this:

    ONTASK_XAPI_EVENTS = {
        "edx.grades.problem.submitted": {
            "context": [
                "course_id",
                "user_id",
                "weight",
                "weight_earned",
                "weight_possible",
            ],
            "data": [
                "problem_id",
            ],
        },
        "problem_check": {
            "context": [
                "course_id",
                "user_id",
            ],
            "data": [
                "problem_id",
            ],
        },
    }
    So the columns for the data frame will be the union of all the context and data fields for each event.
    """
    ontask_xapi_events = getattr(settings, "ONTASK_XAPI_EVENTS", {})

    columns = ["name"]

    for _, event_data in ontask_xapi_events.items():
        columns.extend(event_data["context"])
        columns.extend(event_data["data"])

    return list(set(columns))


def prepare_data_frame(data_frame, course_id, queue, data_frame_columns):
    """
    Create in-memory data frame to be sent to OnTask Learning.

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

    current_batch = queue[course_id]
    for index, event in enumerate(current_batch):
        for key in data_frame_columns:
            data_frame["data_frame"][key][str(index)] = event.get(key)

    return data_frame


def _format_event_for_ontask(event):
    """
    Format the event to be sent to the OnTask Learning installation.

    Args:
        event (dict): The event to format. We expect the event to look like this:

        {
            "name": "edx.grades.problem.submitted",
            "context": {
                "course_id": "course-v1:edX+DemoX+Demo_Course",
                "user_id": "6",
                "weight": 1,
                "weight_earned": 1,
                "weight_possible": 1,
                MORE CONTEXT FIELDS HERE
            },
            "data": {
                "problem_id": "block-v1:eduNEXT+demo-course-2+2023+type@problem+block@d5cf8925c4b8463a95b8ffb0e8875822"
                MORE DATA FIELDS HERE
            },

    Returns:
        dict: The formatted event looking like this:

        {
            "name": "edx.grades.problem.submitted",
            "course_id": "course-v1:edX+DemoX+Demo_Course",
            "user_id": "edXID",
            "weight": 1,
            "weight_earned": 1,
            "weight_possible": 1,
            "problem_id": "block-v1:eduNEXT+demo-course-2+2023+type@problem+block@d5cf8925c4b8463a95b8ffb0e8875822"
        }

        where the fields are the ones configured in the ONTASK_XAPI_EVENTS setting.
    """
    event_column_definition = getattr(
        settings,
        "ONTASK_XAPI_EVENTS", {}).get(event.get("name"),
        {}
    )
    event_context = event.get("context", {})
    event_data = event.get("data", {})
    formatted_event = {
        "name": event.get("name", None), # TODO: try adding another fields from the events here. Configurable?
    }

    for member in event_column_definition["context"]:
        if member in event_context:
            formatted_event[member] = event_context[member]

    for member in event_column_definition["data"]:
        if member in event_data:
            formatted_event[member] = event_data[member]

    return formatted_event


def append_event_to_batch(event, queues):
    """
    Append the event (formatted) to the batch of events to be sent to the OnTask Learning installation.

    Args:
        event (dict): The event to append to the batch.
    """
    formatted_event = _format_event_for_ontask(event)
    current_course_id = formatted_event.get("course_id", None)
    course_queue = queues.get(current_course_id, [])
    course_queue.append(formatted_event)
    queues[current_course_id] = course_queue
