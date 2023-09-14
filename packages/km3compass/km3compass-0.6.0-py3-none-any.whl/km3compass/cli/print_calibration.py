#!/usr/bin/env python3
"""
Command line interface to display compass calibration

Usage:
    compass_print_calibration --det SERIAL
    compass_print_calibration (-h | --help)
    compass_print_calibration --version

Options:
    --det SERIAL       Display calibrations for detector with <SERIAL>
    -h --help          Show this screen.

Example:
    compass_print_calibration --det 49
"""

from docopt import docopt
import km3compass as kc
import pandas as pd
import km3db
import numpy as np


def get_detector(serial):
    """
    Return modules composing the detector with provided serial
    """

    sds = km3db.tools.StreamDS(container="pd")
    df = sds.detectors(SERIALNUMBER=49)
    if df.shape[0] > 1:
        raise Exception(
            "More than one detector with serial number = '{}' in DB !!".format(serial)
        )

    print("Detector with serial '{}' found:".format(serial))
    print(df)

    det = sds.clbmap(detoid=df["OID"].iloc[0])

    return det


def cli_display_calibration():
    """
    Actual fonction doing the job here
    """

    args = docopt(__doc__, version=kc.version)
    db_agent = kc.calibration_DB_agent()

    if args["--det"] is not None:
        serial = int(args["--det"])
        det = get_detector(serial)

        # Remove base module
        # det = det[det["FLOORID"] != 0]

        # Format position into a nice string
        det["Position"] = (
            det["DUID"].astype(str).str.pad(width=4, side="left", fillchar="0")
        )
        det["Position"] += "."
        det["Position"] += (
            det["FLOORID"].astype(str).str.pad(width=2, side="left", fillchar="0")
        )
        det["Position"] += ".37"
        det.set_index("Position", inplace=True)

        # Change column name
        det.rename(columns={"UPI": "CLB UPI"}, inplace=True)

        # Attach DOMs UPI to the table
        DOM_upis = db_agent.sds.integration(
            container_upi="3.4/*", content_upi="3.4.3.2/*"
        )
        map_CLB2DOM = DOM_upis.set_index("CONTENT_UPI")["CONTAINER_UPI"].to_dict()
        det["DOM UPI"] = det["CLB UPI"].replace(map_CLB2DOM)

        # Attach compass UPI

        # make a "Base module proof wrapper
        def get_compass_UPI(CLB_UPI):
            try:
                return db_agent.get_compass_UPI(CLB_UPI)
            except:
                return ""

        det["compass UPI"] = det["CLB UPI"].apply(get_compass_UPI)

        # Create empty column for calibration related info
        det["FIRMWARE_VERSION"] = np.full(det.shape[0], "", dtype=str)
        det["Calib version"] = np.zeros(det.shape[0], dtype=int)
        det["TESTOPID"] = np.full(det.shape[0], "", dtype=str)

        # Loop over DOMs to add calibration info
        for ind in det.index:
            compass_UPI = det.loc[ind]["compass UPI"]

            if compass_UPI == "":
                print("CLB {} : associated compass UPI not found. Ignore the CLB.")
                continue

            compass_SN = int(compass_UPI.split(".")[-1])

            # Some compass don't have calibration
            if compass_SN not in db_agent.calibs["SERIALNUMBER"].values:
                continue

            # Parse information
            calib = db_agent.get_calibration(compass_SN)
            det.at[ind, "FIRMWARE_VERSION"] = calib["FIRMWARE_VERSION"]
            det.at[ind, "Calib V"] = int(calib["TESTNAME"].split("v")[-1])
            det.at[ind, "TESTOPID"] = calib["TESTOPID"]

        # Only keep DOM with calibration
        det = det[det["TESTOPID"] != ""]

        # Sort per index
        det = det.sort_index()

        # Display the table
        cols = [
            "DOM UPI",
            "CLB UPI",
            "compass UPI",
            "FIRMWARE_VERSION",
            "Calib V",
            "TESTOPID",
        ]

        formatters = {}

        for col in cols:
            formatters[col] = "{{:<{}s}}".format(
                det[col].astype(str).str.len().max()
            ).format
        print(formatters)

        print(
            det.astype(str).to_string(
                columns=cols, formatters=formatters, justify="right"
            )
        )

        # print(det.to_string(, justify="right"))
