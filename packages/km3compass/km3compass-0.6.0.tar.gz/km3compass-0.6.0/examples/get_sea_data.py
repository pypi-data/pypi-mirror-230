"""
How to download a large batch of sea data
=========================================

This example propose a simple script to download a large number of
runs from the DB. In this example, the full ORCA6 period is download
and save inside a h5 file.
"""

import km3compass as kc
import km3db as kb
import numpy as np
import pandas as pd

#####################################################
# Get the runs range
# ~~~~~~~~~~~~~~~~~~
#
# This first block show how to retrieve the detector version
# information, containing the detector serial number as well as the
# range of runs that can be requested.
#
# You need to know the det OID, that can also be found in the DB.

detoid = "D_ORCA006"


sds = kb.tools.StreamDS(container="pd")  # Get access to StreamDS
detector = sds.detectors(OID=detoid)  # Get entry for given detoid

# Get a list of runs for the given detector
df_runs = sds.runs(detid=detector.SERIALNUMBER[0])

# Get the min and max run from that
minrun = np.min(df_runs["RUN"])
maxrun = np.max(df_runs["RUN"])


#####################################################
# Download the data (optional)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# This is where it will take some time ... A 6h run can take up to 10
# minutes, but it would be wise to first start your script on few runs
# to check the download speed. Also, consider that downloading 1 year
# of data will represent a peak memory usage between 10GB and 15GB. It
# might be useful to separate the downloading in slices when dealing
# with a very long time period.

reader = kc.readerOnline(detoid, minrun=minrun, maxrun=maxrun)

#####################################################
# Apply calibration to data (optional)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# This is not mandatory, but in this example we decide to go for a
# prepared dataset where the stored information is already calibrated.

db_agent = kc.calibration_DB_agent()
det_calib = kc.detector_calibration(reader, db_agent=db_agent)
det_calib.apply_calibration()

#####################################################
# Resample the dataset (optional)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# If stored directly, the dataset will take few tens of GB of disk
# space, with its sampling frequency of 0.1Hz. This is unecessary,
# because the DOM movement are more of the order of the few hours or
# days scale. To reduce the fluctuation from the measurements as well
# as the size of the output file, we decide to resample to a
# measurement per DOM per 10 minutes.
#
# ``resample_df`` function will do that, by computing the average by
# slice of 10 minutes. See pandas.DataFrame.resample function if you
# want to know more.

df = kc.resample_df(det_calib.df, period="10min")


#####################################################
# Saving the dataset on disk
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Finally, we can save the dataset to an h5 file.  We also save some
# metadata that might be useful for later analysis.


filename = "output_calibrated.h5"

store = pd.HDFStore(filename)

# Save the detector configuration
store["detector"] = detector
# Save the list of runs from DB
store["df_runs"] = df_runs
# Save the calibration information
store["df_calib"] = det_calib.summary
# Save the calibrated and resampled dataset
store["df"] = df
