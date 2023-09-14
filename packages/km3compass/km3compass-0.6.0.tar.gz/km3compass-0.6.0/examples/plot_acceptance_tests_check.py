"""
How to use acceptance test module
=================================

The following example shows how to use the ``acceptance_test`` class 
to retrieve the interest parameter for the acceptance tests procdure.

"""
import km3compass as kc
import matplotlib.pyplot as plt
import pandas as pd

#####################################################
# Get some calibrated data
# ~~~~~~~~~~~~~~~~~~~~~~~~
#
# This is done quickly. Please take a look at the proper
# examples if you want details about that.
filename = "../tests/DOM_0801.csk"
reader = kc.readerCSK(filename)
calib = kc.calib_DB(reader, 817302522)

#####################################################
# Apply acceptance tests routine
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# This routine will first correct the data from a possible
# miss-alignment between the xy plane, by ensuring that acceleration
# is orthogonal to xy data plane. Then, it will agregate the
# measurements per cardinal points using DBSCAN clustering
# algorithm. When it is done, we should have 4 clusters. For each of
# these, the average position is computed and will be used later to
# determine the residual in a polar coordinate system.

accept = kc.acceptance_test(calib, 817302522)


#####################################################
# Display results from the test
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Here we are using pandas to do a nice formating of the output:

print(pd.DataFrame(accept.residuals, index=[817302522]))

#####################################################
# Draw summary plot
# ~~~~~~~~~~~~~~~~~
#
# This summary plot shows the data used in ``acceptance_test``:

accept.plot_results()


plt.show()
