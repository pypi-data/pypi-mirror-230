#!/usr/bin/env python3
"""
Command line interface to generate calibration with km3compass

Usage:
    generate_calibration --upi UPI [--dummy-calibration --json JSON_FILE --jpp JPP_FILE --display]
    generate_calibration (-h | --help)
    generate_calibration --version

Options:
    --upi UPI             Compass UPI
    --json JSON_FILE      Output a json file in JSON_FILE
    --jpp JPP_FILE        Output a jpp-formated file in JPP_FILE
    --display             Print the calibration in humand-readable format
    --dummy-calibration   Produce a dummy calibration
    -h --help             Show this screen.

Example:
    generate_calibration --upi 3.4.3.4/AHRS/1.69
"""

from docopt import docopt
import km3compass as kc
import pandas as pd
import km3db
import numpy as np


def generate_calibration(
    compass_UPI, json_file=None, jpp_file=None, dummy_calibration=False, display=False
):
    compass_SN = int(compass_UPI.split(".")[-1])
    calibration = kc.calibration_object(
        compass_UPI=compass_UPI,
        compass_SN=compass_SN,
        source=f"km3compass-{kc.version}/generate_calibration",
    )

    if dummy_calibration:
        calibration.set("type", kc.CALIBRATION_TYPE_UNITY)
    else:
        raise NotImplementedError("Only dummy_calibration implemented !")

    if json_file:
        print(f"Export calibration to json in {json_file} ")
        calibration.to_json(filename=json_file, with_test_session=True)

    if jpp_file:
        print(f"Export calibration to jpp format in {jpp_file} ")
        calibration.to_jpp(filename=jpp_file)

    if display:
        print(calibration)


def main():
    args = docopt(__doc__, version=kc.version)

    dummy_calibration = args["--dummy-calibration"]
    compass_UPI = args["--upi"]
    json_file = args["--json"]
    jpp_file = args["--jpp"]
    display = args["--display"]

    generate_calibration(
        compass_UPI,
        dummy_calibration=dummy_calibration,
        json_file=json_file,
        jpp_file=jpp_file,
        display=display,
    )


if __name__ == "__main__":
    main()
