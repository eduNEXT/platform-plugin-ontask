"""
Open edX Filters needed for OnTask integration.
"""

import pkg_resources
from django.conf import settings
from django.template import Context, Template
from openedx_filters import PipelineStep
from web_fragments.fragment import Fragment

TEMPLATE_ABSOLUTE_PATH = "/instructor_dashboard/"
BLOCK_CATEGORY = "ontask"


class AddInstructorOnTaskTab(PipelineStep):
    """Add Ontask tab to instructor dashboard."""

    def run_filter(self, context, template_name):  # pylint: disable=arguments-differ
        """Execute filter that modifies the instructor dashboard context.

        Args:
            context (dict): the context for the instructor dashboard.
            template_name (str): instructor dashboard template name.
        """
        course = context["course"]
        template = Template(self.resource_string("static/html/ontask.html"))
        context.update(
            {
                "ontask_url": settings.ONTASK_URL,
                "workflow_id": course.other_course_settings.get("ontaskWorkflowId"),
            }
        )
        html = template.render(Context(context))
        frag = Fragment(html)

        frag.add_css(self.resource_string("static/css/ontask.css"))

        section_data = {
            "fragment": frag,
            "section_key": BLOCK_CATEGORY,
            "section_display_name": "On Task",
            "course_id": str(course.id),
            "template_path_prefix": TEMPLATE_ABSOLUTE_PATH,
        }
        context["sections"].append(section_data)
        return {
            "context": context,
            "template_name": template_name,
        }

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string("platform_plugin_ontask", path)
        return data.decode("utf8")
