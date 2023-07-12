"""
Open edX Filters needed for OnTask integration.
"""
# from crum import get_current_request
from openedx_filters import PipelineStep
from web_fragments.fragment import Fragment
from django.template import Context, Template
import pkg_resources

from django.conf import settings

TEMPLATE_ABSOLUTE_PATH = "/instructor_dashboard/"
BLOCK_CATEGORY = "ontask"

class AddInstructorLimesurveyTab(PipelineStep):
    """Add Ontask tab to instructor dashboard."""

    def run_filter(self, context, template_name):  # pylint: disable=unused-argument, arguments-differ
        """Execute filter that modifies the instructor dashboard context.

        Args:
            context (dict): the context for the instructor dashboard.
            _ (str): instructor dashboard template name.
        """
        course = context["course"]
        data = pkg_resources.resource_string("platform_plugin_ontask", "static/ontask.html")
        template_str = data.decode("utf-8")
        template = Template(template_str)
        context.update({
            "ONTASK_URL": getattr(settings, "ONTASK_URL"),
        })
        html = template.render(Context(context))
        frag = Fragment(html)

        section_data = {
            "fragment": frag,
            "section_key": BLOCK_CATEGORY,
            "section_display_name": "On Task",
            "course_id": str(course.id),
            "template_path_prefix": TEMPLATE_ABSOLUTE_PATH,
        }
        context["sections"].append(section_data)
        return context
