"""
How to use ellipsoid calibration module
=======================================

This example shows how the initial calibration for compasses can be
produced using an ellipsoid fit on data. These data are expected to
cover rotation along the 3 axis.
"""

import km3compass as kc
import matplotlib.pyplot as plt

#####################################################
# Loading some data
# ~~~~~~~~~~~~~~~~~
#
# Load some calibration data
filename = "../tests/compass_3_1101_calibration.csk"
reader = kc.readerCSK(filename)
print(reader.module_IDs)

#####################################################
#
# For illustration purpose, let's display the raw data from the CSK
# file :

fig, axes = plt.subplots(3, 1, sharex=True)

for i in range(3):
    mag_label = f"AHRS_H{i}"
    axes[i].scatter(reader.df["datetime"], reader.df[mag_label])
    axes[i].set_ylabel(mag_label)
    axes[i].grid()

axes[-1].set_xlabel("Time")

plt.tight_layout()

#####################################################
# Apply the calibration procedure
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# The procedure is applid with `calibration_ellipsoid_fit`.
# The result is then recovered as `calibration_object`

cal = kc.calibration_ellipsoid_fit(reader)
calibration = cal.calibration
print(calibration)


#####################################################
# Export the result as a json string
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# The ``calibration_object`` embed a `to_json` method that convert the
# calibration in json directly.  This method return a json_str, and if
# a `filename` is provided as argument will also save it in a file.

json_str = calibration.to_json("test_calib_km3ant.json")
print(json_str)


#####################################################
# Applying the produced calibration
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# To apply this calibration to the data, the ``calibration_module`` is
# used :

calibrated_data = kc.calibration_module(reader, reader.module_IDs[0], calibration)

#####################################################
#
# The resulting object can be used to display the calibrated data:

fig, axes = plt.subplots(3, 1, sharex=True)

for i in range(3):
    mag_label = f"AHRS_H{i}"
    axes[i].scatter(calibrated_data.df["datetime"], calibrated_data.df[mag_label])
    axes[i].set_ylabel(mag_label)
    axes[i].grid()

axes[-1].set_xlabel("Time")

plt.tight_layout()
