"""
How to use calib DB module
==========================

The following example shows how to use the ``calib_DB`` class,
using an acceptance tests measurement (60 seconds measurement
with the DOM oriented in each of the 4 cardinal points).

This calibration module will use the module ID to retrieve the proper
compass calibration in the km3 central DB.

"""
import km3compass as kc
import matplotlib.pyplot as plt

#####################################################
# Loading some data
# ~~~~~~~~~~~~~~~~~
# Initialising is a simple as this:
filename = "../tests/DOM_0801.csk"
reader = kc.readerCSK(filename)
print(reader.module_IDs)

#####################################################
# Applying calibration
# ~~~~~~~~~~~~~~~~~~~~
# The ``calib_DB`` is a quite easy object to handle.  It expects as
# input a python class with a property ``.df``, that contains a
# ``pandas.DataFrame`` with columns :
# ``['hx','hy','hz','ax','ay','az','moduleID']``.  Also, this module
# expects only one module, so you should provide the the module ID you
# want to use.

calib = kc.calib_DB(reader, 817302522)

#####################################################
# Print calibration information
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Data (both acceleration and magnetic field) are calibrated by first
# applying an offset (3D vector) to the data, followed by a rotation matrix (3x3 matrix). Both
# of this elements can be displayed using embeded functions.

calib.print_calibration()


#####################################################
# Comparing data before and after calibration
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# To do so, we will use the ``kc.plot_raw_results`` function, that
# works for both raw and calibrated data :

kc.plot_raw_results(reader.df, title="Data before calibration")

kc.plot_raw_results(calib.df, title="Data after applying DB calibration")


#####################################################
#
# Comparing the results before and after calibration, we can already
# see that the magnetic field seems now to be centered around a point
# close to 0, which is what we expect. In the case of the acceptance
# tests, we know that the rotation should be only the XY plan but we
# can see that some of the movement seems to be along the Z
# direction. Looking at the right most plot, we can see that the
# acceleration is not fully aligned with the Z axis (i.e. angle is not
# 90°). To correct this, we can manually correct this using the
# accelerometer information.
#
#
# Aligning Z direction with weight
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# **Strictly speaking, this part is not a calibration, but more a
# correction. Don't use it blindly, only if it makes sense
# !**Schematically, what we want is to rotate all the measurement to
# have the weight (i.e. full acceleration) aligned with the Z axis. To
# do so, a function is provided in km3compass : ``kc.align_z2weight``


df = kc.align_z2weight(calib.df)

kc.plot_raw_results(
    df, title="Data after applying calibration and aligning weight with Z"
)


plt.show()
