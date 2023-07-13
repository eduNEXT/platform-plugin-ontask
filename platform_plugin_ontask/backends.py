from collections import defaultdict
from django.conf import settings

from platform_plugin_ontask.utilities import precompute_data_frame_columns, prepare_data_frame, get_workflow_data_frame, update_workflow_data_frame
from xmodule.modulestore.django import modulestore
from opaque_keys.edx.keys import CourseKey

class OnTaskRoutingBackend:
    """
    Event tracker backend that emits sends data to an OnTask Learning installation.
    """

    def __init__(self, **kwargs):
        """
        Event tracker backend that emits an Open edX public signal.
        """
        self.queue = defaultdict(list)
        self.batch_size = getattr(
            settings,
            "ONTASK_TRACKING_BACKEND_BATCH_SIZE",
            1,
        )
        self.data_frame_columns = precompute_data_frame_columns()

    def _send_batch(self, course_id, workflow_id):
        """
        Send a batch of events to the OnTask Learning installation.
        """
        print("Sending batch of {} events to OnTask Learning".format(len(self.queue)))
        print("Sending events to OnTask Learning: {}".format(self.queue))
        current_data_frame = get_workflow_data_frame(workflow_id)
        print("Current data frame in OnTask Learning: {}".format(current_data_frame))
        new_data_frame = prepare_data_frame(
            current_data_frame,
            course_id,
            self.queue,
            self.data_frame_columns,
        )
        print("Sending data frame to OnTask Learning: {}".format(new_data_frame))
        update_workflow_data_frame(workflow_id, new_data_frame)
        self.queue = defaultdict(list)

    def _format_event(self, event):
        """
        Format the event to be sent to the OnTask Learning installation.

        Args:
            event (dict): The event to format.
        """
        event_column_definition = getattr(
            settings,
            "ONTASK_XAPI_EVENTS", {}).get(event.get("name"),
            {}
        )
        event_context = event.get("context", {})
        event_data = event.get("event", {})
        formatted_event = {
            "name": event.get("name", None), # TODO: try adding another fields from the events here. Configurable?
        }

        for member in event_column_definition["context"]:
            formatted_event[member] = event_context.get(member, None)

        for member in event_column_definition["event"]:
            formatted_event[member] = event_data.get(member, None)

        return formatted_event

    def _append_event_to_batch(self, event):
        """
        Append the event to the batch of events to be sent to the OnTask Learning installation.

        Args:
            event (dict): The event to append to the batch.
        """
        formatted_event = self._format_event(event)
        current_course_id = formatted_event.get("course_id", None)
        self.queue[current_course_id].append(formatted_event)

    def send(self, event):
        """
        Send the event to the OnTask Learning installation.
        """
        event_name = event.get("name", None)
        if not getattr(settings, "ONTASK_XAPI_EVENTS", {}).get(event_name):
            print("Event {} not found in ONTASK_XAPI_EVENTS, skipping event.".format(event_name))
            return

        event_context = event.get("context", {})
        course_id = event_context.get("course_id", None)

        if not course_id:
            print("No course ID found in event context, skipping event.")
            return

        course_key = CourseKey.from_string(course_id)
        course = modulestore().get_course(course_key, depth=0)
        other_course_settings = course.other_course_settings

        ontask_workflow_id = other_course_settings.get("ontask_workflow")
        if not ontask_workflow_id:
            print("No OnTask Learning workflow found for course, skipping event.")
            return

        self._append_event_to_batch(event)

        if len(self.queue[course_id]) >= self.batch_size:
            self._send_batch(course_id, ontask_workflow_id)
