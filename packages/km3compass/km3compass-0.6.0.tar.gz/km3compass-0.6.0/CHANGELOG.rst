Unreleased changes
------------------

* Added ``compass_generation_calibration`` CLI tool to produce calibration. Only work with dummy calibration for now.
* Added jpp format as possible output to ``calibration_object``.
* Changed minimum python version to 3.8 to comply with recent pandas versions.

>>>>>>> origin
Version 0
---------  

0.5.0 / 2023-03-24
~~~~~~~~~~~~~~~~~~
* Added ``zero_calibration`` module, which apply no-calibration while mimicking the process. It can be used with ``detector_calibration`` to produce a set of data for a given detector ID, without applying any calibration. 

0.4.1 / 2023-02-09
~~~~~~~~~~~~~~~~~~
* Fixed non-communicated value of the calibration by the DB, previously set to Nan, now set to "N.C." (see #5).


0.4.0 / 2023-01-27
~~~~~~~~~~~~~~~~~~
* Added support for ``calib_from_expected_field``, providing calibration from sea-data.
* Fixed tagging of missing calibration in ``detector_calibration``
* Added ``CHANGELOG.rst`` usage

  
0.1.0 / 2021-07-09
~~~~~~~~~~~~~~~~~~
* Project generated using the cookiecutter template from
  https://git.km3net.de/templates/python-project
