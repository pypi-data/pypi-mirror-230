#!/usr/bin/env python3
import km3db
import numpy as np
import pandas as pd

from .calibration_object import calibration_object


class calibration_DB_agent:
    """
    Handle DB request to speed up things.
    To avoid duplicating DB connection, this class is a singleton.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(calibration_DB_agent, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        print("Starting a new calibration DB agent ...")
        start = np.datetime64("now")
        self.sds = km3db.tools.StreamDS(container="pd")
        self.CLB_UPIs = self.sds.clbid()
        self.calibs = self.sds.ahrscalib().sort_values(["REVTIMEORDER"])
        self.calibs = self.calibs.fillna("N.C.")
        self.load_CLB2CompassMap()
        print("Done in {}".format(str(np.datetime64("now") - start)))

    def load_CLB2CompassMap(self):
        """Load the table to create CLB to compass map"""
        df = self.sds.integration(CONTENT_UPI="*AHRS*")
        df = pd.concat((df, self.sds.integration(CONTENT_UPI="*LSM303*")))
        self.compass = df[
            (df["CONTENT_UPI"].str.contains("AHRS"))
            | (df["CONTENT_UPI"].str.contains("LSM303"))
        ]
        self.compass = self.compass.set_index("CONTAINER_UPI")
        self.compass["COMPASS_SN"] = [
            int(upi.split(".")[-1]) for upi in self.compass["CONTENT_UPI"]
        ]
        CLB_info = self.CLB_UPIs.set_index("CLBUPI").loc[self.compass.index]
        self.compass = pd.concat((self.compass, CLB_info), axis=1).reset_index()

    def get_CLB_UPI(self, mac_address):
        """
        Return CLB UPI from mac address

        Parameters:
        -----------
        mac_address: str
          DOM mac address, lower case expected.
        """
        df = self.CLB_UPIs[self.CLB_UPIs["MACADDR"].str.lower() == mac_address]
        return df.iloc[0]["CLBUPI"]

    def get_compass_UPI(self, CLB_UPI):
        """
        Return compass UPI from CLB UPI

        Compass calibration is selected by taking the smaller
        REVTIMEORDER for a given compass serial number. More details
        in this git issue:
        https://git.km3net.de/common/km3web/-/issues/46#note_21808

        Parameters:
        -----------
        CLB UPI: str
          CLB UPI in string format
        """
        df = self.compass[self.compass["CONTAINER_UPI"] == CLB_UPI]
        return df.iloc[0]["CONTENT_UPI"]

    def get_compass_UPI_from_modID(self, moduleID):
        """
        Return compass UPI from module ID

        Compass calibration is selected by taking the smaller
        REVTIMEORDER for a given compass serial number. More details
        in this git issue:
        https://git.km3net.de/common/km3web/-/issues/46#note_21808

        Parameters:
        -----------
        module ID: int
          DOM module ID (integer, derived from mac address)
        """
        df = self.compass[self.compass["CLBID"] == moduleID]
        return df.iloc[0]["CONTENT_UPI"]

    def get_calibration(self, compass_SN):
        """
        Return calibration object from compass serial number

        Parameters:
        -----------
        compass_SN: int
          Compass serial number
        """
        df = self.calibs[self.calibs["SERIALNUMBER"] == compass_SN]
        c = df.iloc[0]  # Take the smaller REVTIMEORDER

        cobj = calibration_object(
            compass_SN=c["SERIALNUMBER"], type=c["TESTNAME"], source="DB", parent=c
        )

        # Add norm
        A_rot = np.zeros((3, 3))
        H_rot = np.zeros((3, 3))
        G_rot = np.zeros((3, 3))

        A_offsets = np.zeros(3)
        H_offsets = np.zeros(3)

        for i, ii in enumerate(["X", "Y", "Z"]):
            A_offsets[i] = c[f"ACC_OFFSET_{ii}"]
            H_offsets[i] = np.mean([c[f"MAG_{ii}MIN"], c[f"MAG_{ii}MAX"]])

            for j, jj in enumerate(["X", "Y", "Z"]):
                A_rot[i, j] = c[f"ACC_ROT_{ii}{jj}"]
                H_rot[i, j] = c[f"MAG_ROT_{ii}{jj}"]
                G_rot[i, j] = c[f"GYRO_ROT_{ii}{jj}"]

        cobj.set("A_rot", A_rot)
        cobj.set("H_rot", H_rot)
        cobj.set("G_rot", G_rot)
        cobj.set("A_offsets", A_offsets)
        cobj.set("H_offsets", H_offsets)

        return cobj
