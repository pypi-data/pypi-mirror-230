#!/usr/bin/env python3
import km3db
import numpy as np
import pandas as pd

import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from .tools import cart2AHRS, modID2mac
from .toolsDB import calibration_DB_agent
from .calibration_object import calibration_object
from .version import version

from scipy.optimize import leastsq
import time


class calibration_module:
    """
    Generic module to apply a calibration on a reader object

    Parameters:
    -----------
    reader: km3compass reader object
      Reader object, either CSK or -something else-
    moduleID: int
      DOM module ID inside the file.
    calibration: ``km3compass.calibration_object``
      Calibration object to be used.
    calibrate: bool, default = True
      Apply or not the calibration. Can be turned off to modify calibration.
    db_agent: calibration_DB_agent object
      Provide external calibration_DB_agent object, avoiding additional query to DB
    """

    def __init__(
        self,
        reader,
        moduleID,
        calibration,
        calibrate=True,
        db_agent=None,
        verbosity=True,
    ):
        self.moduleID = moduleID
        self.calibration = calibration
        self.db_agent = db_agent
        if self.db_agent is None:
            self.db_agent = calibration_DB_agent()
        self.verbosity = verbosity
        self.status = False

        self.row_calib = None
        self.mac_address = modID2mac(self.moduleID)
        self.get_compass_info()

        if calibration is not None:
            self.status = True

        self.df = reader.df
        self.df = self.df[self.df["DOMID"] == self.moduleID].copy()

        if self.verbosity:
            print("DOM mac address : {}".format(self.mac_address))

        if calibrate and calibration is not None:
            try:
                self.apply_calibration()
            except Exception as E:
                if verbosity:
                    print(E)
                self.df = None

    def apply_calibration(self):
        """
        Apply calibration on df.

        Equivalent to the implementation in JPP ``JDETECTOR::JCompass::JCompass``
        https://common.pages.km3net.de/jpp/classJDETECTOR_1_1JCompass.html
        """

        if self.status == False:
            raise Exception("Non-valid calibration, can't apply calibration.")

        a = self.df[["AHRS_A0", "AHRS_A1", "AHRS_A2"]].values
        a_calibrated = (
            self.calibration.get("A_rot")
            .dot((a + (-self.calibration.get("A_offsets"))[np.newaxis, :]).T)
            .T
        )

        h = self.df[["AHRS_H0", "AHRS_H1", "AHRS_H2"]].values
        h_calibrated = (
            self.calibration.get("H_rot")
            .dot((h + (-self.calibration.get("H_offsets"))[np.newaxis, :]).T)
            .T
        )

        for i in range(3):
            self.df["AHRS_A{}".format(i)] = a_calibrated[:, i]
            self.df["AHRS_H{}".format(i)] = h_calibrated[:, i]

    def print_calibration(self):
        """Print a summary of the calibration file"""
        print(self.calibration)

    def get_summary_df(self):
        """Return a calibration summary dataframe"""
        df = pd.DataFrame(
            {
                "DOMID": [self.moduleID],
                "Variant": [self.compassVariant],
                "CLB UPI": [self.CLB_UPI],
                "Compass UPI": [self.compass_UPI],
                "status": [self.status],
            }
        ).set_index("DOMID")

        calib = self.row_calib

        if calib is not None:
            calib["DOMID"] = self.moduleID
            calib = self.row_calib.to_frame().T.set_index("DOMID")

        return pd.concat((df, calib), axis=1)

    def get_compass_info(self):
        # Get CLB UPI
        self.CLB_UPI = self.db_agent.get_CLB_UPI(self.mac_address)

        # Get Compass UPI
        self.compass_UPI = None
        self.compassSN = 0
        self.compassVariant = "UNKNOWN"

        try:
            self.compass_UPI = self.db_agent.get_compass_UPI(self.CLB_UPI)
        except:
            print("Impossible to find compass:")
            print(f"\tDOM mac address = {self.mac_address}")
            print(f"\tCLB UPI = {self.CLB_UPI}")
            self.row_calib = pd.Series(
                {
                    "TESTNAME": "Unknown compass",
                    "DOMID": self.moduleID,
                    "FIRMWARE_VERSION": "-",
                }
            )
            return
        # Extract compass serial number
        self.compassSN = int(self.compass_UPI.split(".")[-1])
        self.compassVariant = self.compass_UPI.split("/")[1]


class calib_DB(calibration_module):
    """
    Module for applying calibration from DB

    Parameters:
    -----------
    reader: km3compass reader object
      Reader object, either CSK or -something else-
    moduleID: int
      DOM module ID inside the file.
    calibrate: bool, default = True
      Apply or not the calibration. Can be turned off to modify calibration.
    db_agent: calibration_DB_agent object
      Provide external calibration_DB_agent object, avoiding additional query to DB
    verbosity: bool
      Toggle verbosity during the calibration process
    """

    def __init__(self, reader, moduleID, calibrate=True, db_agent=None, verbosity=True):
        # Calling parent init without calibration prepare everything
        # but doesn't apply calibration, ignoring calibrate argument
        super().__init__(reader, moduleID, None, calibrate, db_agent, verbosity)

        # Call DB to load calibration
        self.load_calibration()

        if calibrate and self.status:
            self.apply_calibration()

    def calibrate(self):
        """Apply calibration chain"""
        self.load_calibration()
        self.apply_calibration()

    def load_calibration(self):
        """
        Load calibration from km3net webdb

        This is done in steps :
        #. Mac address conversion to CLB UPI
        #. CLB UPI to compass UPI
        #. Get calibration from ahrscalib streamDS
        """

        # Check if floor ID == 0
        # If yes, it's a base module : no calibration
        if "FLOORID" in self.df.columns:
            if self.df.FLOORID.iloc[0] == 0:
                print(
                    "No calibration expected, {} is a base module.".format(
                        self.moduleID
                    )
                )
                self.row_calib = pd.Series(
                    {
                        "TESTNAME": "No calib (Base module)",
                        "DOMID": self.moduleID,
                        "FIRMWARE_VERSION": "-",
                    }
                )
                return

        # Get the calib from ahrscalib streamDS
        try:
            self.calibration = self.db_agent.get_calibration(self.compassSN)
            self.row_calib = self.calibration.get("parent")
        except:
            print("Impossible to find calibration:")
            print(f"\tDOM mac address = {self.mac_address}")
            print(f"\tCLB UPI = {self.CLB_UPI}")
            print(f"\tCompass SN = {self.compassSN}")
            self.row_calib = pd.Series(
                {
                    "TESTNAME": "No calibration",
                    "DOMID": self.moduleID,
                    "FIRMWARE_VERSION": "-",
                }
            )
            return

        self.status = True


class calib_self_sphere:
    """
    Module to try calibrate from data itself

    Parameters:
    -----------
    reader: km3compass reader object
      Reader object, either CSK or -something else-
    moduleID: int
      DOM module ID inside the file.
    calibrate: bool, default = True
      Apply or not the calibration. Can be turned off to modify calibration.
    """

    def __init__(self, reader, moduleID):
        self.moduleID = moduleID
        self.reader = reader
        self.df = reader.df
        self.df = self.df[self.df["DOMID"] == self.moduleID]

        self.fit_result = self.sphere_fit(
            self.df["AHRS_H0"].values,
            self.df["AHRS_H1"].values,
            self.df["AHRS_H2"].values,
        )

        self.fit_result = np.array(self.fit_result)

        self.center = self.fit_result[1:]
        self.radius = self.fit_result[0]
        self.status = True
        self.apply_calibration()

    def sphere_fit(self, spX, spY, spZ):
        """
        Function to fit a sphere to a 3D set of points

        Full credit to Charles Jekel (https://jekel.me/2015/Least-Squares-Sphere-Fit/)

        Parameters:
        -----------
        spX : numpy array
          X coordinates
        spY : numpy array
          Y coordinates
        spZ : numpy array
          Z coordinates


        Return:
        -------
        Radius, Cx, Cy, Cz
          Radius and x,y,z coordinate of the sphere center
        """
        #   Assemble the A matrix
        spX = np.array(spX)
        spY = np.array(spY)
        spZ = np.array(spZ)
        A = np.zeros((len(spX), 4))
        A[:, 0] = spX * 2
        A[:, 1] = spY * 2
        A[:, 2] = spZ * 2
        A[:, 3] = 1

        #   Assemble the f matrix
        f = np.zeros((len(spX), 1))
        f[:, 0] = (spX * spX) + (spY * spY) + (spZ * spZ)
        C, residules, rank, singval = np.linalg.lstsq(A, f, rcond=None)

        #   solve for the radius
        t = (C[0] * C[0]) + (C[1] * C[1]) + (C[2] * C[2]) + C[3]
        radius = np.sqrt(t)

        return radius, C[0], C[1], C[2]

    def apply_calibration(self):
        """Apply calibration determined with sphere fit"""

        for i, axe in enumerate(["AHRS_H0", "AHRS_H1", "AHRS_H2"]):
            self.df[axe] -= self.center[i]

    def plot_results(self):
        """Plot summary of the fit process"""

        fig = plt.figure(figsize=(12, 6))

        spec = mpl.gridspec.GridSpec(2, 4, fig)

        axe3D = fig.add_subplot(spec[:, :2], projection="3d")
        axeR = fig.add_subplot(spec[0, 3])

        u, v = np.mgrid[0 : 2 * np.pi : 20j, 0 : np.pi : 10j]
        x = self.radius * np.cos(u) * np.sin(v) + self.center[0]
        y = self.radius * np.sin(u) * np.sin(v) + self.center[1]
        z = self.radius * np.cos(v) + self.center[2]
        axe3D.plot_wireframe(x, y, z, color="C0", linewidth=1)
        axe3D.set_aspect("auto")
        axe3D.set_xlabel("X [G]")
        axe3D.set_ylabel("Y [G]")
        axe3D.set_zlabel("Z [G]")

        df_raw = self.reader.df
        axe3D.scatter(
            df_raw["AHRS_H0"],
            df_raw["AHRS_H1"],
            df_raw["AHRS_H2"],
            color="C3",
            marker=".",
        )

        r = np.sqrt(
            self.df["AHRS_H0"] ** 2 + self.df["AHRS_H1"] ** 2 + self.df["AHRS_H2"] ** 2
        )
        residuals = (r - self.radius) / self.radius * 100.0
        bins = np.linspace(np.min(residuals) * 1.5, np.max(residuals) * 1.5, 21)
        axeR.hist(residuals, bins=bins, histtype="stepfilled", alpha=0.6)
        axeR.set_xlabel("Radius residuals [%]")

        plt.tight_layout()


class zero_calibration(calibration_module):
    """
    Module to apply empty calibration

    Parameters:
    -----------
    reader: km3compass reader object
      Reader object, either CSK or -something else-
    moduleID: int
      DOM module ID inside the file.
    calibrate: bool, default = True
      Apply or not the calibration. Can be turned off to modify calibration.
    db_agent: calibration_DB_agent object
      Provide external calibration_DB_agent object, avoiding additional query to DB
    verbosity: bool
      Toggle verbosity during the calibration process
    """

    def __init__(self, reader, moduleID, calibrate=True, db_agent=None, verbosity=True):
        super().__init__(reader, moduleID, None, calibrate, db_agent, verbosity)
        self.calibration = calibration_object(
            compass_SN=self.compassSN,
            compass_UPI=self.compass_UPI,
            type="Empty_calibration",
            source=f"km3compass-{version}",
        )

        self.status = True
        self.row_calib = pd.Series(
            {
                "TESTNAME": "empty_calibration",
                "DOMID": self.moduleID,
                "FIRMWARE_VERSION": "-",
            }
        )
        print(self.get_summary_df())
        print(self.calibration)

        if calibrate and self.status:
            self.apply_calibration()


class detector_calibration:
    """
    Module to calibrate a sea dataset

    This module will iterate over the present module and apply
    calibration. It also produces summary information and provides
    filtering methods.

    Parameters:
    -----------
    reader: km3compass reader object
      Reader object, either CSK or -something else-
    moduleID: int
      DOM module ID inside the file.
    calibrate: bool, default = True
      Apply or not the calibration. Can be turned off to modify calibration.
    """

    def __init__(self, reader, db_agent=None, calib_module=calib_DB, verbosity=True):
        self.reader = reader
        self.db_agent = db_agent
        self.calib_module = calib_module
        self.verbosity = verbosity

        if self.db_agent is None:
            self.db_agent = calibration_DB_agent()

    def apply_calibration(self):
        """Apply calibration to the provided reader"""

        def get_mod_information(df, modID):
            df = df[df["DOMID"] == modID]
            return df.iloc[[0]][["DOMID", "FLOORID", "DUID"]].set_index("DOMID")

        self.df = None
        self.summary = None
        self.calib_dict = {}

        # Loop over modules
        for modID in np.unique(self.reader.df["DOMID"]):
            calib = self.calib_module(
                self.reader,
                int(modID),
                db_agent=self.db_agent,
                verbosity=self.verbosity,
            )

            self.calib_dict[modID] = calib
            # Create a summary row with calibration information
            summary_row = calib.get_summary_df()
            summary_row = pd.concat(
                (summary_row, get_mod_information(self.reader.df, modID)), axis=1
            )
            # Store summary row
            self.summary = pd.concat((self.summary, summary_row))

            # Calibration not done, pass to next DOM
            if calib.df is None:
                continue
            # Calibration done, store calibrated data in self.df
            self.df = pd.concat((self.df, calib.df), axis=0)

    def print_calibration_summary(self):
        """Print a summary of calibration"""
        n_DOM = len(np.unique(self.reader.df[self.reader.df["FLOORID"] > 0]["DOMID"]))
        n_BM = len(np.unique(self.reader.df[self.reader.df["FLOORID"] == 0]["DOMID"]))

        n_DOM_ok = len(np.unique(self.summary[self.summary["status"]].index))

        print("DOM/BM before calibration: {}/{}".format(n_DOM, n_BM))
        print("DOM after calibration: {}".format(n_DOM_ok))
        print("Details about calibration:")

        self.df_overview = self.summary
        self.df_overview.replace({"0.0": "0"}, inplace=True)
        self.df_overview["n compass"] = np.ones(self.summary.shape[0], dtype=int)
        self.df_overview = self.df_overview.groupby(
            ["DUID", "TESTNAME", "Variant", "FIRMWARE_VERSION"]
        ).sum()["n compass"]
        print("\n" + "-" * 10 + " Summary per DU " + "-" * 10)
        print(self.df_overview.to_string())

        self.df_overview = self.summary
        self.df_overview.replace({"0.0": "0"}, inplace=True)
        self.df_overview["n compass"] = np.ones(self.summary.shape[0], dtype=int)
        self.df_overview = self.df_overview.groupby(
            ["TESTNAME", "Variant", "FIRMWARE_VERSION"]
        ).sum()["n compass"]
        print("\n" + "-" * 10 + " Summary full detector " + "-" * 10)
        print(self.df_overview.to_string())

    def plot_calibration_summary(self):
        """Plot a summary of calibration version per DOM"""

        DUID_map = {}
        for i, duid in enumerate(np.unique(self.summary["DUID"].values)):
            DUID_map[duid] = i

        fig, axe = plt.subplots()
        axe.set_aspect("equal")
        axe.set_xlim((-1, 19))
        axe.set_ylim((-1, len(DUID_map)))

        nodata_kwargs = {
            "hatch": "",
            "edgecolor": [0.4] * 3,
            "facecolor": [0, 0, 0, 0],
            "zorder": 0,
        }
        nocal_kwargs = {
            "hatch": "//",
            "edgecolor": [0.4] * 3,
            "facecolor": [0, 0, 0, 0],
            "zorder": 1,
        }

        def plot_category(coords, axe, kwargs, label=""):
            first = True
            for coord in coords:
                coord = coord.astype(float) - 0.5
                patch = mpl.patches.Rectangle(coord, 1, 1, **kwargs)
                if first:
                    patch = mpl.patches.Rectangle(coord, 1, 1, label=label, **kwargs)
                    first = False
                axe.add_patch(patch)

        df = self.summary[self.summary["status"] == False].copy()

        df["DUID"] = df["DUID"].replace(DUID_map)

        full_array = np.meshgrid(np.arange(19), np.arange(len(DUID_map)))
        full_array = np.reshape(full_array, (2, len(DUID_map) * 19))
        full_array = np.swapaxes(full_array, 0, 1)

        plot_category(
            full_array,
            axe,
            nodata_kwargs,
            label="No data",
        )
        plot_category(
            df[["FLOORID", "DUID"]].values,
            axe,
            nocal_kwargs,
            label="No calibration",
        )

        for it, ind in enumerate(self.df_overview.index):
            label = "{}, calib V{}, fw {}".format(ind[1], ind[0][-1], ind[2])
            kwargs = {"edgecolor": [0.4] * 3, "facecolor": "C" + str(it), "zorder": 1}

            if ind[2] == "-":
                label = "{}, no calibration".format(ind[1])
                kwargs["alpha"] = 0.2
            df = self.summary[
                (self.summary["TESTNAME"] == ind[0])
                & (self.summary["Variant"] == ind[1])
                & ((self.summary["FIRMWARE_VERSION"] == ind[2]))
            ].copy()

            df["DUID"] = df["DUID"].replace(DUID_map)
            plot_category(df[["FLOORID", "DUID"]].values, axe, kwargs, label=label)

        axe.set_yticks(list(DUID_map.values()))
        axe.set_yticklabels(list(DUID_map.keys()))
        axe.set_xticks(np.linspace(0, 18, 10, dtype=int))
        axe.set_xlabel("Floor ID")
        axe.set_ylabel("DU ID")

        axe.legend(
            bbox_to_anchor=(0, 1.02, 1, 0.2),
            loc="lower left",
            mode="expand",
            borderaxespad=0,
            ncol=2,
        )

        plt.tight_layout()

        return fig


def ellipsoid_fit(x, y, z):
    """
    Perform ellipsoid fit on 3D data x y z

    This implementation is copied from matlab code written by Ozan Aktas.
    Original code can be found here : https://diydrones.com/forum/topics/compansating-hardiron-soft-iron-and-scaling-effects-in-magnetic

    Parameters:
    -----------
    x, y and z: arrays
      3D coordinates of the data points

    Return:
    -------
    norm: float
      radius of the average sphere
    offsets: 3D array
      x,y & z center offsets of the ellipsoid
    W_inverted: 3x3 arrray
      Matrix to pass from ellipsoid to sphere
    """

    # n data points x 9 ellipsoid parameters
    D = np.array(
        [
            x**2,
            y**2,
            z**2,
            2.0 * x * y,
            2.0 * x * z,
            2.0 * y * z,
            2.0 * x,
            2.0 * y,
            2.0 * z,
        ]
    ).T

    # solve the normal system of equations and find fitted ellipsoid parameters
    v = np.linalg.solve(
        np.matmul(D.T, D), np.matmul(D.T, np.ones((D.shape[0], 1)))
    ).flatten()

    #  form the algebraic form of the ellipsoid
    A = np.array(
        [
            [v[0], v[3], v[4], v[6]],
            [v[3], v[1], v[5], v[7]],
            [v[4], v[5], v[2], v[8]],
            [v[6], v[7], v[8], -1],
        ]
    )

    # find the center of the ellipsoid
    offsets = np.linalg.solve(A[0:3, 0:3], v[6:9])

    # remove offset, do same calculation again written in a simplified algebraic form of elipsoid
    x = x + offsets[0]
    y = y + offsets[1]
    z = z + offsets[2]

    K = np.array([x**2, y**2, z**2, 2.0 * x * y, 2.0 * x * z, 2.0 * y * z]).T

    # solve the normal system of equation
    p = np.linalg.solve(
        np.matmul(K.T, K), np.matmul(K.T, np.ones((K.shape[0], 1)))
    ).flatten()

    # form the algebraic form of the ellipsoid with center at (0,0,0)
    AA = np.array([[p[0], p[3], p[4]], [p[3], p[1], p[5]], [p[4], p[5], p[2]]])

    # solve the eigenproblem
    evals, evecs = np.linalg.eig(AA)
    radii = np.sqrt(1.0 / evals)
    norm = (radii[0] * radii[1] * radii[2]) ** (1.0 / 3.0)

    # calculate transformation matrix elipsoidal to spherical
    W_inverted = np.matmul(evecs * np.sqrt(evals), np.linalg.inv(evecs) * norm)

    return norm, offsets, W_inverted


class calibration_ellipsoid_fit:
    """
    Generate calibration from raw data, using ellipsoid fit

    Parameters:
    -----------
    reader: km3compass reader object
      Reader object, either CSK or -something else-
    moduleID: int
      DOM module ID inside the file.
    compass_SN: int
      Compass serial number
    """

    def __init__(self, reader, moduleID=None, compass_SN=None):
        self.raw_data = reader
        self.df = self.raw_data.df
        self.moduleID = moduleID
        # No module ID provided, try to extract it
        if self.moduleID is None:
            mods = self.df["DOMID"].unique()
            if len(mods) != 1:
                raise Exception(
                    "No moduleID provided, but more than 1 available in raw data !"
                )
            self.moduleID = mods[0]

        self.compass_SN = compass_SN
        # If no compass SN provided, get it from moduleID
        if self.compass_SN is None:
            mac_address = modID2mac(self.moduleID)
            db = calibration_DB_agent()
            CLB_UPI = db.get_CLB_UPI(mac_address)
            self.compass_UPI = db.get_compass_UPI(CLB_UPI)
            self.compass_SN = int(self.compass_UPI.split(".")[-1])

        # Create an empty calibration object to store later results
        self.calibration = None
        self.fit_data()

    def fit_data(self):
        """Apply ellipsoid fit on accelerometer and compass data"""

        self.A_norm, self.A_offsets, self.A_rot = ellipsoid_fit(
            self.df["AHRS_A0"].values,
            self.df["AHRS_A1"].values,
            self.df["AHRS_A2"].values,
        )
        self.H_norm, self.H_offsets, self.H_rot = ellipsoid_fit(
            self.df["AHRS_H0"].values,
            self.df["AHRS_H1"].values,
            self.df["AHRS_H2"].values,
        )
        self.calibration = calibration_object(
            compass_SN=self.compass_SN,
            compass_UPI=self.compass_UPI,
            type="AHRS-CALIBRATION-v4",
            source=f"km3compass-{version}",
            A_norm=self.A_norm,
            A_offsets=-self.A_offsets,
            A_rot=self.A_rot,
            H_norm=self.H_norm,
            H_offsets=-self.H_offsets,
            H_rot=self.H_rot,
        )

    def get_calibration(self):
        """Return calibration module"""
        return self.calibration


class calib_from_expected_field:
    """
    Module that calibrates compasses from sea data

    Parameters:
    -----------
    reader: km3compass reader object
      Reader object, either CSK or -something else-
    moduleID: int
      DOM module ID inside the file.
    """

    def __init__(self, reader, moduleID, compassSN=None):
        self.df = reader.df
        du = self.df.loc[self.df["DOMID"] == moduleID, "DUID"].iloc[0]
        # compass data of other DOMs in same DU for mean calculation
        du_df = self.df[self.df["DUID"] == du]
        # a copy that can be accessed in functions
        self.du_df = du_df
        # compass data only of DOM we are calibrating
        self.df = self.df[self.df["DOMID"] == moduleID]
        self.df = self.df.dropna(subset=["AHRS_H0", "AHRS_H1", "AHRS_H2"])

        # magnetic fields of DOM with ID moduleID
        h_x = self.df["AHRS_H0"].values
        h_y = self.df["AHRS_H1"].values
        h_z = self.df["AHRS_H2"].values

        # select neighbouring DOMs
        doms = self.select_neigbouring_doms(moduleID)
        self.db = calibration_DB_agent()

        # here are computed the mean magnetic fields in each direction and the field norm
        h_x_mean, h_y_mean, h_z_mean, r_mean = self.mean_mag_fields(
            int(moduleID), doms, reader
        )

        # here we subtract this mean field in each direction
        mean_x = float(np.mean(h_x)) - h_x_mean
        mean_y = float(np.mean(h_y)) - h_y_mean
        mean_z = float(np.mean(h_z)) - h_z_mean

        # least square fitting done here
        """
        NB doing the lsq fit actually worsens the results
           commented out for now
        self.fit_result = self.sphere_fit(
            h_x,
            h_y,
            h_z,
            r_mean, mean_x, mean_y, mean_z
        )
        """
        fit_result = np.array([r_mean, mean_x, mean_y, mean_z])
        self.center = fit_result[1:]
        self.radius = fit_result[0]
        # storing in calibration object
        self.compass_SN = compassSN

        # If no compass SN provided, get it from moduleID
        if self.compass_SN is None:
            self.compass_UPI = self.db.get_compass_UPI_from_modID(moduleID)
            self.compass_SN = int(self.compass_UPI.split(".")[-1])

        self.make_calibration_object(moduleID, reader)

    def select_neigbouring_doms(self, moduleID, n_neighbors=2):
        """
        select neigbouring DOMs to the one currently calibrated
        Parameters:
        -----------
        moduleID: int
          DOM module ID inside the file.
        n_neighbors: int (defaul: 2)
          Number of DOMs taken on each side.
        Return:
        -------
        doms: numpy array
          array of neigbouring DOMIDs
        """
        du_df = self.du_df
        floor = int(du_df.loc[du_df["DOMID"] == moduleID, "FLOORID"].iloc[0])

        if floor < 1 + n_neighbors:
            floor = 1 + n_neighbors

        elif floor > 18 - n_neighbors:
            floor = 18 - n_neighbors

        du_df = du_df[
            (du_df["FLOORID"] <= floor + n_neighbors)
            & (du_df["FLOORID"] >= floor - n_neighbors)
        ]

        doms = du_df.DOMID.unique().astype(int)
        return doms

    def mean_mag_fields(self, moduleID, doms, reader, cut_radius=0.015):
        """
        compute mean magnetic field in each direction, using calibrated magnetometer data
        uses only compasses in the same DU (passed with doms array, contains dom IDs in same DU)
        uses only compasses of the same variant
        rejects miscalibrated DOMs: the norm of the magnetic field is used as a control parameter
        for miscalibrated DOMs
        Parameters:
        -----------
        moduleID: int
          DOM module ID inside the file.
        doms: numpy array
          The neigbouring DOMs to use in computation of the expected field
        reader: km3compass reader object
          Reader object, either CSK or -something else-
        Return:
        -------
        mean H_0, mean H_1, mean H_2, mean magnetic field norm
         The mean magnetic field along each axis and the mean norm as experienced by neighbouring DOMs
        """
        moduleID = int(moduleID)
        # Calibrate all the DOMs available in the reader
        calib_df = detector_calibration(reader, verbosity=False)
        calib_df.apply_calibration()

        df = calib_df.df
        df["DOMID"] = df["DOMID"].astype(int)

        # field norms
        df["AHRS_HR"] = np.sqrt(
            df["AHRS_H0"] ** 2 + df["AHRS_H1"] ** 2 + df["AHRS_H2"] ** 2
        )

        doms = [
            d for d in doms if d != moduleID
        ]  # Generate the list of DOMs, excluding target DOM
        # check if the neigbouring DOMs are correctly calibrated
        for dom in doms:
            to_drop = (
                calib_df.summary.loc[dom]["status"] == False
                or df[df["DOMID"] == dom]["AHRS_HR"].std() >= cut_radius
            )
            print(dom, to_drop)
            if to_drop:
                df.drop(df[df["DOMID"] == dom].index)

        # Reduce the df to one line per DOM, that contains the mean value of the field
        df = df.groupby("DOMID").mean(numeric_only=True).reset_index()

        # Use the CLBUPI, added when calibrating, to add the compassUPI
        def fail_proof_compass_UPI(domID):
            try:
                return self.db.get_compass_UPI_from_modID(domID)
            except Exception as E:
                print(f"Impossible to get Compass UPI for {domID}: {E}")
                return np.nan

        df["Compass_UPI"] = df["DOMID"].apply(fail_proof_compass_UPI)
        df = df.dropna(subset=["Compass_UPI"])

        # Declare and use a function to convert compass_UPI to
        def CompassUPI_to_variant(upi):
            return upi.split("/")[1]

        df["Compass_variant"] = df["Compass_UPI"].apply(CompassUPI_to_variant)

        df = df.set_index("DOMID")

        temp_array = df.index.to_numpy(dtype=int)
        # check if all elements of array doms are in dataframe
        for dom in list(doms):
            ind = np.where(temp_array == dom)
            ind = np.array(ind)
            if ind.size == 0:
                ind2 = np.where(doms == dom)
                doms = np.delete(doms, ind2)
        doms = [float(i) for i in doms]
        target_dom = df.loc[moduleID]
        df = df.loc[doms]  # Reduce the list to the neighbor DOMs
        return (
            df["AHRS_H0"].mean(),
            df["AHRS_H1"].mean(),
            df["AHRS_H2"].mean(),
            df["AHRS_HR"].mean(),
        )

    def make_calibration_object(self, moduleID, reader):
        """
        creates calibration object

        Parameters:
        -----------
        moduleID: int
          DOM module ID inside the file.
        reader: km3compass reader object
          Reader object, either CSK or -something else-
        """

        calib_df = calib_DB(reader, moduleID, calibrate=True)
        """
        get temporary calibration object to fetch calibration constants we do not compute:
        A_norm, A_offsets, A_rot
        H_norm, H_rot: if compass fails acceptance tests, can we trust these parameters?
        """
        self.calibration = None
        calibration_temp = self.db.get_calibration(self.compass_SN)
        self.A_norm = calibration_temp.get("A_norm")
        self.A_offsets = calibration_temp.get("A_offsets")
        self.A_rot = calibration_temp.get("A_rot")
        # self.H_norm = calibration_temp.get("H_norm")
        self.H_rot = calibration_temp.get("H_rot")
        self.H_offsets = self.center
        self.H_norm = self.radius

        # NB: change calibration type to some agreed-upon value
        self.calibration = calibration_object(
            compass_SN=self.compass_SN,
            compass_UPI=self.compass_UPI,
            type="AHRS-SEA-CALIBRATION-v1",
            source=f"km3compass-{version}",
            A_norm=self.A_norm,
            A_offsets=-self.A_offsets,
            A_rot=self.A_rot,
            H_norm=1.0,
            H_offsets=-self.H_offsets,
            H_rot=np.identity(3),
        )
