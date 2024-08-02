Platform Plugin OnTask
########################

|ci-badge| |license-badge| |status-badge|


Purpose
*******

Open edX plugin that includes adds a new tab to the instructor dashboard for
easy access to the OnTask service. Also, it includes an API to create a new
workflow and table in OnTask based on the course data. For serving OnTask along
with the Open edX ecosystem we recommended using `tutor-contrib-ontask`_.

This plugin has been created as an open source contribution to the Open edX
platform and has been funded by the Unidigital project from the Spanish
Government - 2024.

.. _tutor-contrib-ontask: https://github.com/eduNEXT/tutor-contrib-ontask/

Compatibility Notes
===================

+------------------+--------------+
| Open edX Release | Version      |
+==================+==============+
| Palm             | >= 0.2.0     |
+------------------+--------------+
| Quince           | >= 0.2.0     |
+------------------+--------------+
| Redwood          | >= 0.2.0     |
+------------------+--------------+

The settings can be changed in ``platform_plugin_ontask/settings/common.py``
or, for example, in tutor configurations.

**NOTE**: the current ``common.py`` works with Open edX Palm, Quince and
Redwood version.


Getting Started
***************

Developing
==========

One Time Setup
--------------

Clone the repository:

.. code-block:: bash

  git clone git@github.com:eduNEXT/platform-plugin-ontask.git
  cd platform-plugin-ontask

Set up a virtualenv with the same name as the repo and activate it. Here's how
you might do that if you have ``virtualenv`` set up:

.. code-block:: bash

  virtualenv -p python3.8 platform-plugin-ontask

Every time you develop something in this repo
---------------------------------------------

Activate the virtualenv. Here's how you might do that if you're using
``virtualenv``:

.. code-block:: bash

  source platform-plugin-ontask/bin/activate

Grab the latest code:

.. code-block:: bash

  git checkout main
  git pull

Install/update the dev requirements:

.. code-block:: bash

  make requirements

Run the tests and quality checks (to verify the status before you make any
changes):

.. code-block:: bash

  make validate

Make a new branch for your changes:

.. code-block:: bash

  git checkout -b <your_github_username>/<short_description>

Using your favorite editor, edit the code to make your change:

.. code-block:: bash

  vim ...

Run your new tests:

.. code-block:: bash

  pytest ./path/to/new/tests

Run all the tests and quality checks:

.. code-block:: bash

  make validate

Commit all your changes, push your branch to github, and open a PR:

.. code-block:: bash

  git commit ...
  git push

Deploying
==========

Tutor environments
------------------

To use this plugin in a Tutor environment, you must install it as a requirement
of the ``openedx`` image. To achieve this, follow these steps:

.. code-block:: bash

    tutor config save --append OPENEDX_EXTRA_PIP_REQUIREMENTS=git+https://github.com/edunext/platform-plugin-ontask@vX.Y.Z
    tutor images build openedx

Then, deploy the resultant image in your environment.


Using the API
*************

The API endpoint is protected with the same auth method as the Open edX
platform. For generate a token, you can use the next endpoint:

- **POST** ``/<lms_host>/oauth2/access_token/``: Generate a token for the user.
  The content type of the request must be ``application/x-www-form-urlencoded``.

  **Body parameters**

  - ``client_id``: Client ID of the OAuth2 application. You can find it in the
    Django admin panel. Normally, it is ``login-service-client-id``.
  - ``grant_type``: Grant type of the OAuth2 application. Normally, it is
    ``password``.
  - ``username``: Username of the user.
  - ``password``: Password of the user.
  - ``token_type``: Type of the token. By default, it is ``bearer``

  Alternatively, you can use a new OAuth2 application. You can create a new
  application in the Django admin panel. The body parameters are the same as
  the previous endpoint, but you must use the ``client_id`` and ``client_secret``
  of the new application. The ``grant_type`` must be ``client_credentials``.

  **Response**

  - ``access_token``: Access token of the user. You must use this token in the
    ``Authorization`` header of the requests to the API.

Finally, you are ready to use the API. The next endpoints are available:

- **POST** ``/<lms_host>/platform-plugin-ontask/<course_id>/api/v1/workflow/``:
  Create a new workflow in OnTask. This also creates a new table in the workflow.

  **Path parameters**

  - **course_id (Required)**: ID of the course.

- **PUT** ``/<lms_host>/platform-plugin-ontask/<course_id>/api/v1/table/``:
  Updates the current table in a OnTask workflow. This performs a merge of the
  current table with the new data.

  **Path parameters**

  - **course_id (Required)**: ID of the course.


Configuring required in the Open edX platform
*********************************************

You must include the following setting in the LMS to enable the filter that
will display add the new tab for OnTask:

.. code-block:: python

    OPEN_EDX_FILTERS_CONFIG = {
        "org.openedx.learning.instructor.dashboard.render.started.v1": {
            "fail_silently": False,
            "pipeline": [
                "platform_plugin_ontask.extensions.filters.AddInstructorOnTaskTab",
            ]
        },
    }

It is also necessary to include these settings for each course using the
**Other Course Settings** in the **Advanced Settings** section in Studio:

- **ONTASK_API_AUTH_TOKEN** *(Optional)*: API Auth token for the OnTask
  service. You can find it in the OnTask service from **Profile** >
  **API Auth token**. If the token has not been generated, you can create
  a new one.
- **ONTASK_WORKFLOW_ID** *(Optional)*: ID of the workflow in OnTask. If you
  already have a workflow, you can include it here. If you do not have a
  workflow, the plugin will create a new one from the OnTask tab in the
  instructor dashboard.

Example:

.. code-block:: json

  {
    ...
    "ONTASK_API_AUTH_TOKEN": "your-api-auth-token",
    "ONTASK_WORKFLOW_ID": 1
  }

**NOTE**: It is posible to configure the **ONTASK_API_AUTH_TOKEN** at platform
level. You can include it in the LMS settings. This way, you do not need to
configure it in each course.

**NOTE**: It is important to have enabled the **Other Course Settings** in the
settings of the platform. You can find more information about this in the
`Open edX documentation`_.

.. _Open edX documentation: https://edx.readthedocs.io/projects/edx-installing-configuring-and-running/en/latest/configuration/enable_custom_course_settings.html


View from the Learning Management System (LMS)
**********************************************

When the instructor accesses the OnTask tab, they will have the option to
create an OnTask Workflow in case there is not one configured. Once the
**Create Workflow** button is clicked, a workflow will be created in OnTask and
will be named as the current course ID. e.g. ``course-v1:edunext+ontask+demo``.

.. image:: https://github.com/user-attachments/assets/efc836ac-bdbb-4857-8791-cfb1602b820f

The instructor can then view the OnTask workflow related to the course. From
there the instructor can create, import/export or execute all actions. In the
upper left corner there will be a button called **Load Data**. Once pressed, an
asynchronous task will be executed that will generate a data summary of the
course and load it into a table in the OnTask Workflow. Each time the button is
pressed, the data will be recreated. The instructor can then use this data to
create different actions.

.. image:: https://github.com/user-attachments/assets/c7d4fe5c-c2d0-4d81-975d-1766912568c1

Once the data has been loaded, the instructor can go to **Table** > **View
data**. There the instructor find the table with all the data summary of the
course.

.. image:: https://github.com/user-attachments/assets/05a416d6-a29f-4fbd-9508-61ed8b9575c5


Create a Custom Data Summary Backend
*********************************************

By default, the data summary loaded into the OnTask table is generated from the
course completion and grade data. These are the columns that are loaded into
the OnTask table:

- ``user_id`` *(Integer)*: ID of the user.
- ``username`` *(String)*: Username of the user.
- ``email`` *(String)*: Email of the user.
- ``course_id`` *(String)*: ID of the course.
- ``unit_{unit_id}_name`` *(String)*: Name of the unit.
- ``unit_{unit_id}_completed`` *(Boolean)*: If the unit is completed.
- ``component_{component_id}_grade`` *(Float)*: Grade of the component.

You can create a custom data summary backend to add new columns to the data
summary that is loaded into the OnTask table. To do this, follow these steps:

1. Create a new file in the ``data_summary`` directory with the name of the
   backend, e.g., ``custom.py``
2. Create a class that inherits from ``DataSummary``, e.g.,
   ``CustomDataSummary(DataSummary)``
3. Implement the ``get_data_summary`` method to return the data summary. The
   method must return a dictionary where each key is the column name and the
   value is other dictionary with the ID as key, and the value as the value of
   the column.

   .. code-block:: python

      class CustomDataSummary(DataSummary):
        """Custom data summary for example purposes."""

        def get_data_summary(self) -> dict:
          """
          Get a custom data summary.

          Returns:
              dict: A custom data summary.
          """
          data_frame = {
              "user_id": {"0": 1},
              "unit_a7e390b77964476fb9924f0bc194da4c_custom_value": {"0": False},
              "unit_a7e390b77964476fb9924f0bc194da4c_another_custom_value": {"0": "value"},
          }
          return data_frame

   **NOTE**: The dataframe must include at least the ``user_id`` column. This
   is important when merge the data with the current OnTask table.

4. Edit the ``ONTASK_DATA_SUMMARY_CLASSES`` setting in the ``common.py`` file
   to include the new backend in the list of backends.

   .. code-block:: python

      settings.ONTASK_DATA_SUMMARY_CLASSES = [
        # ...Another data summary backends
        "platform_plugin_ontask.datasummary.backends.custom.CustomDataSummary"
      ]

   **NOTE**: The ``UnitCompletionDataSummary`` and ``ComponentGradeDataSummary``
   are the default data summary backends. If you do not want to use them, you
   can do so by removing them from the ``ONTASK_DATA_SUMMARY_CLASSES`` setting.

Getting Help
************

If you're having trouble, we have discussion forums at `discussions`_ where you
can connect with others in the community.

Our real-time conversations are on Slack. You can request a
`Slack invitation`_, then join our `community Slack workspace`_.

For anything non-trivial, the best path is to open an `issue`_ in this
repository with as many details about the issue you are facing as you
can provide.

For more information about these options, see the `Getting Help`_ page.

.. _discussions: https://discuss.openedx.org
.. _Slack invitation: https://openedx.org/slack
.. _community Slack workspace: https://openedx.slack.com/
.. _issue: https://github.com/eduNEXT/platform-plugin-ontask/issues
.. _Getting Help: https://openedx.org/getting-help


License
*******

The code in this repository is licensed under the AGPL 3.0 unless
otherwise noted.

Please see `LICENSE.txt <LICENSE.txt>`_ for details.


Contributing
************

Contributions are very welcome. Please read `How To Contribute`_ for details.

This project is currently accepting all types of contributions, bug fixes,
security fixes, maintenance work, or new features.  However, please make sure
to have a discussion about your new feature idea with the maintainers prior to
beginning development to maximize the chances of your change being accepted.
You can start a conversation by creating a new issue on this repo summarizing
your idea.

.. _How To Contribute: https://openedx.org/r/how-to-contribute

Reporting Security Issues
*************************

Please do not report security issues in public. Please email security@edunext.co.

.. It's not required by our contractor at the moment but can be published later
.. .. |pypi-badge| image:: https://img.shields.io/pypi/v/platform-plugin-ontask.svg
    :target: https://pypi.python.org/pypi/platform-plugin-ontask/
    :alt: PyPI

.. |ci-badge| image:: https://github.com/eduNEXT/platform-plugin-ontask/actions/workflows/ci.yml/badge.svg?branch=main
    :target: https://github.com/eduNEXT/platform-plugin-ontask/actions
    :alt: CI

.. |license-badge| image:: https://img.shields.io/github/license/eduNEXT/platform-plugin-ontask.svg
    :target: https://github.com/eduNEXT/platform-plugin-ontask/blob/main/LICENSE.txt
    :alt: License

..  |status-badge| image:: https://img.shields.io/badge/Status-Maintained-brightgreen
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Experimental-yellow
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Deprecated-orange
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Unsupported-red
