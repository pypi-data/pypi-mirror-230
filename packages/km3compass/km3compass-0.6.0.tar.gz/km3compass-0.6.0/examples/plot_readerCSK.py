"""
How to use reader for CSK
=========================

The following example shows how to use the `readerCSK` class,
using a acceptance tests measurement (60 seconds measurement
with the DOM oriented in each of the 4 cardinal points).
"""
from km3compass import readerCSK

#####################################################
# Initialising a readerCSK
# -------------------------
# Initialising is a simple as this:
filename = "../tests/DOM_0801.csk"
reader = readerCSK(filename)

#####################################################
# Access file content
# ~~~~~~~~~~~~~~~~~~~~~
#
# File content is extracted and converted in a pandas
# `DataFrame`.
# You can display the content like this:

print(reader.df)

#####################################################
# To get the measured magnetic field and acceleration
# in `numpy.array` format, you can do the following:

a = reader.df[["AHRS_A0", "AHRS_A1", "AHRS_A2"]].values
h = reader.df[["AHRS_H0", "AHRS_H1", "AHRS_H2"]].values

import numpy as np

print(np.shape(a), np.shape(h))


#####################################################
# Draw a simple plot
# ~~~~~~~~~~~~~~~~~~
#
# The raw values can be displayed using matplolib.
# In this simple example, x vs y components of
# magnetic field are plotted. The aspect of x and y
# are set to equal, to get a better representation
# of the cartesian space.

import matplotlib.pyplot as plt

fig, ax = plt.subplots()

ax.scatter(reader.df["AHRS_H0"], reader.df["AHRS_H1"])

ax.set_aspect("equal")

ax.set_xlabel("X [G]")
ax.set_ylabel("Y [G]")
ax.grid()
plt.show()
