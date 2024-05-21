Platform Plugin On Task
########################

|ci-badge| |license-badge| |status-badge|


Purpose
*******

Open edX plugin that includes adds a new tab to the instructor dashboard for easy access 
to the On Task service. For serving On Task along with the Open edX ecosystem we recommended using
`tutor-contrib-ontask <https://github.com/eduNEXT/tutor-contrib-ontask/>`_.

This plugin has been created as an open source contribution to the Open edX
platform and has been funded by the Unidigital project from the Spanish
Government - 2024.

Getting Started
***************

Developing
==========

One Time Setup
--------------

Clone the repository:

.. code-block:: bash

  git clone git@github.com:eduNEXT/platform_plugin_ontask.git
  cd platform_plugin_ontask

Set up a virtualenv with the same name as the repo and activate it. Here's how
you might do that if you have ``virtualenv`` set up:

.. code-block:: bash

  virtualenv -p python3.8 platform_plugin_ontask

Every time you develop something in this repo
---------------------------------------------

Activate the virtualenv. Here's how you might do that if you're using
``virtualenv``:

.. code-block:: bash

  source platform_plugin_ontask/bin/activate

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

To use this plugin in a Tutor environment, you must install it as a requirement of the ``openedx`` image. To achieve this, follow these steps:

.. code-block:: bash

    tutor config save --append OPENEDX_EXTRA_PIP_REQUIREMENTS=git+https://github.com/edunext/platform-plugin-ontask@vX.Y.Z
    tutor images build openedx

Then, deploy the resultant image in your environment.

Configuring required in the Open edX platform
*********************************************

You must include the following setting in the LMS to enable the filter that will
display add the new tab for On Task:

.. code-block:: python

    OPEN_EDX_FILTERS_CONFIG = {
        "org.openedx.learning.instructor.dashboard.render.started.v1": {
            "fail_silently": False,
            "pipeline": [
                "platform_plugin_ontask.extensions.filters.AddInstructorOnTaskTab",
            ]
        },
    }

You can add it using your favorite configuration method. Then, you'll see:

.. image:: https://github.com/eduNEXT/platform-plugin-ontask/assets/64440265/f4d5adbf-8900-49fc-b7ce-dffaf179b3d8
.. image:: https://github.com/eduNEXT/platform-plugin-ontask/assets/64440265/7ed01c38-6651-43eb-a6c5-cb3f774835b1

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
