"""Custom exceptions for the OnTask plugin."""

from platform_plugin_ontask.utils import _


class CustomInvalidKeyError(Exception):
    """The course key is not valid."""

    def __init__(self, message: str = _("The course key is not valid.")) -> None:
        """
        Initialize the exception.

        Args:
            message (str): The error message.
        """
        self.message = message
        super().__init__(self.message)


class CourseNotFoundError(Exception):
    """The course is not found."""

    def __init__(self, message: str = _("The course does not exist.")) -> None:
        """
        Initialize the exception.

        Args:
            message (str): The error message.
        """
        self.message = message
        super().__init__(self.message)


class APIAuthTokenNotSetError(Exception):
    """The OnTask API Auth Token is not set for the course."""

    def __init__(
        self,
        message: str = _(
            "The OnTask API Auth Token is not set for this course. "
            "Please set it in the Advanced Settings of the course."
        ),
    ) -> None:
        """
        Initialize the exception.

        Args:
            message (str): The error message.
        """
        self.message = message
        super().__init__(self.message)


class WorkflowIDNotSetError(Exception):
    """The OnTask Workflow ID is not set for the course."""

    def __init__(
        self,
        message: str = _(
            "The OnTask Workflow ID is not set for this course. "
            "Please set it in the Advanced Settings of the course."
        ),
    ) -> None:
        """
        Initialize the exception.

        Args:
            message (str): The error message.
        """
        self.message = message
        super().__init__(self.message)
