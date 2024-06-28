"""Base class for data summary."""

from abc import ABC, abstractmethod


class DataSummary(ABC):
    """Interface for data summary."""

    def __init__(self, course_id: str):
        self.course_id = course_id

    @abstractmethod
    def get_data_summary(self):
        """Get the data summary."""
