"""
How to use reader for Online data
=================================

The following example shows how to use the `readerOnline` class,
using for reading data from run 9000 to 9002 with ORCA6 detector.
"""
from km3compass import readerOnline

#####################################################
# Initialising a readerOnline
# -------------------------
# Initialising is a simple as this:
reader = readerOnline("D_ORCA006", minrun=9000, maxrun=9000)


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
# It can take some time to load runs from DB. In order to speed up
# this process, the reader feature a save on disk option. It will
# create a h5 file containing the data in a dataframe format

reader.save_df("online_data.h5")

#####################################################
# To load the previously loaded data, a filename as well as the
# filekey should be provided to the reader :


reader = readerOnline(filename="online_data.h5", filekey="runs_9000_9000")

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
