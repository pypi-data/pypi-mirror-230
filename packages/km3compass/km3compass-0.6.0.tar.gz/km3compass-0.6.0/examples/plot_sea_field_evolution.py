"""
Plotting time evolution of magnetic field
=========================================

"""
import pandas as pd
import km3compass as kc
import os
import matplotlib.pyplot as plt
import numpy as np


#####################################################
# Getting some data
# -----------------
#
#  In this example we are downloading 3 runs to look at the magnetic
# field time evolution. You can notice the field ``kwargs_query`` used
# in the reader. Here, we are using it to only focus on the data that
# come from the DU 11, reducing by a factor 6 the amount of data we
# download. Removing this criteria will just lead to the whole detector
# being download.
#
#  In the first code block, we also introduce a bit of intelligence to
# check if the data were already downloaded, avoiding to re-download
# them when already available.

reader = None
filename = "sea_sample.h5"
filekey = "test_sample"
detoid = "D_ORCA006"

if not os.path.isfile(filename):
    reader = kc.readerOnline(
        detoid, minrun=9000, maxrun=9002, kwargs_query={"DUID": 11}
    )
    reader.save_df(filename, filekey)
else:
    reader = kc.readerOnline(filename=filename, filekey=filekey)


#####################################################
# Calibrate the data
# ------------------
#
# In this code block, we are now using the ``detector_calibration``
# object to automatically calibrate all the data coming from our
# detector. This object also contains some summary function, to show
# which DOMs get calibrated, with which version of the calibraiton.

det_calib = kc.detector_calibration(reader)

det_calib.apply_calibration()
det_calib.print_calibration_summary()
det_calib.plot_calibration_summary()


#####################################################
# Resampling the dataset
# ----------------------
#
# The compass data are saved every 10 seconds for these runs. For most
# of the application, where we are looking at effect that takes hours
# to happen, this unnecessary. Here, we will average the value per 10
# minutes slot, in order to reduce the measure fluctuation as well as
# getting a lighter data set.
#
# This done with the ``pandas.DataFrame`` method ``resample``. If you
# don't know about, you should read the doc: this is awesome !

df = None
origin = np.min(det_calib.df["datetime"])

# Will resample separately each DOM, using the same time origin each time.
for modID in np.unique(det_calib.df["DOMID"]):
    df_tmp = det_calib.df[det_calib.df["DOMID"] == modID]
    df_tmp = df_tmp.resample("10min", on="datetime", origin=origin).mean(
        numeric_only=True
    )

    # df_tmp contains the resample value for dom modID
    # Now merging the results in df
    df = pd.concat((df, df_tmp))


#####################################################
# Convert to spherical coordinates
# --------------------------------
#
# Now that our dataset is calibrated and resampled, we can convert the
# x, y & z coordinates of the magnetic field in spherical coordinate,
# more usefull when it comes to look at the DOM positionning

coord_sphere = kc.cart2spherical(df[["AHRS_H0", "AHRS_H1", "AHRS_H2"]].values)
df["r"] = coord_sphere[:, 0]
df["phi"] = kc.rad2deg(coord_sphere[:, 1])
df["theta"] = kc.rad2deg(coord_sphere[:, 2])

# We also all rows that contains nan, just in case.
df = df.dropna(axis=0)


#####################################################
# Plotting the time evolution
# ---------------------------
#
# Here we are plotting 3 differents parameters in function of time :
# r, phi and theta. We define a coloscale that goes from 0 to 18 and
# that will represent the different DOMs along the DU.

for duid in np.unique(df["DUID"]):
    fig, axes = plt.subplots(3, 1, figsize=[6, 6], sharex=True)

    fig.suptitle("DU {}".format(int(duid)))

    axes[0].set_ylabel("phi (z) [deg]")
    axes[1].set_ylabel("theta (x:y) [deg]")
    axes[2].set_ylabel("Norm [G]")

    ind = df["DUID"] == duid

    kwargs = {
        "marker": ".",
        "c": df["FLOORID"][ind],
        "vmin": 0,
        "vmax": 18,
        "linestyle": "-",
    }

    sc = axes[0].scatter(df.index[ind], df["phi"][ind], **kwargs)
    fig.colorbar(sc, ax=axes[0])
    sc = axes[1].scatter(df.index[ind], df["theta"][ind], **kwargs)
    fig.colorbar(sc, ax=axes[1])
    sc = axes[2].scatter(df.index[ind], df["r"][ind], **kwargs)
    fig.colorbar(sc, ax=axes[2])

    plt.xticks(rotation=45)
    plt.tight_layout()

plt.show()
