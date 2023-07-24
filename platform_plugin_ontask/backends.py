import logging
from collections import defaultdict
from django.conf import settings

from xmodule.modulestore.django import modulestore
from opaque_keys.edx.keys import CourseKey

from platform_plugin_ontask.tasks import send_student_data_to_ontask
from platform_plugin_ontask.utilities import append_event_to_batch

log = logging.getLogger(__name__)


class OnTaskRoutingBackend:
    """
    Event tracker backend that emits sends data to an OnTask Learning installation.
    """

    def __init__(self, **kwargs):
        """
        Event tracker backend that emits an Open edX public signal.
        """
        self.queues = {}

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

        batch_size = getattr(
            settings,
            "ONTASK_TRACKING_BACKEND_BATCH_SIZE",
            1,
        )
        course_key = CourseKey.from_string(course_id)
        course = modulestore().get_course(course_key, depth=0)
        other_course_settings = course.other_course_settings

        ontask_workflow_id = other_course_settings.get("ONTASK_COURSE_WORKFLOW_ID")
        if not ontask_workflow_id:
            print("No OnTask Learning workflow found for course, skipping event.")
            return

        append_event_to_batch(event, self.queues)

        if len(self.queues.get(course_id, [])) >= batch_size:
            send_student_data_to_ontask(self.queues, course_id, ontask_workflow_id)
            self.queues[course_id] = []
