"""OnTask API client."""

import requests


class OnTaskClient:
    """Client to interact with the OnTask API."""

    def __init__(self, api_url: str, api_key: str):
        """
        Initialize the OnTask client.

        Arguments:
            api_url (str): The OnTask API URL.
            api_key (str): The OnTask API key.
        """
        self.api_url = api_url
        self.api_key = api_key
        self.headers = {"Authorization": f"Token {self.api_key}"}
        self.timeout = 5

    def create_workflow(self, course_id: str) -> requests.Response:
        """
        Create an OnTask workflow.

        Arguments:
            course_id (str): The course ID.

        Returns:
            requests.Response: The response object.
        """
        return requests.post(
            url=f"{self.api_url}/workflow/workflows/",
            json={"name": course_id},
            headers=self.headers,
            timeout=self.timeout,
        )

    def update_table(self, workflow_id: str, data_frame: dict) -> requests.Response:
        """
        Update an OnTask table.

        Arguments:
            workflow_id (str): The workflow ID.
            data_frame (dict): The data frame to update.

        Returns:
            requests.Response: The response object.
        """
        return requests.put(
            url=f"{self.api_url}/table/{workflow_id}/ops/",
            json={"data_frame": data_frame},
            headers=self.headers,
            timeout=self.timeout,
        )
