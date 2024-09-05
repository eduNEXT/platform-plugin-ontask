Change Log
##########

..
   All enhancements and patches to platform_plugin_ontask will be documented
   in this file.  It adheres to the structure of https://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (https://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
**********

*

0.5.0 - 2024-09-05
**********************************************

Added
======

* Added a new ``UserDataSummary`` backend.

Changed
=======

* Updated the plugin unit tests.
* Updated ``CompletionDataSummary`` and ``ComponentGradeDataSummary`` backend
  so that column names are human readable and unique.


0.4.0 - 2024-08-01
**********************************************

Added
======

* Added support for multiple Data Summary backends.
* Added a Django setting to allow configure the OnTask API Auth token at
  platform level.
* Added a new ``ComponentGradeDataSummary`` backend.

Changed
=======

* Updated the plugin documentation.
* Updated the plugin unit tests.
* Updated ``CompletionDataSummary`` backend. It was renamed to
  ``UnitCompletionDataSummary``.

0.3.0 - 2024-07-16
**********************************************

Added
======

* Added connection with OnTask using the new API.
* Added unit tests for the plugin.
* Added documentation for the plugin.
* Added translation support for the plugin and added Spanish (es_ES and es_419) translation.

0.2.3 – 2024-05-21
**********************************************

Change
======

* Apply quality corrections for better code maintainability.

0.2.2 – 2024-05-17
**********************************************

Added
=====

* Add missing file for settings.

0.2.1 – 2024-05-17
**********************************************

Added
=====

* Remove import that breaks production environment

0.2.0 – 2024-05-16
**********************************************

Added
=====

* Added support for the new version of the platform.

0.1.0 – 2023-07-03
**********************************************

Added
=====

* First release on PyPI.
