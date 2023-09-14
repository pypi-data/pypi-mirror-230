#!/usr/bin/env python3
"""
Command line tool to perform acceptance-test evaluation of compass.
The input file can contains multiple DOMs.

Usage:
    compass_display_csk FILENAME [--no-w-cor --csv-calib FNAME --csv-raw FNAME]
    compass_display_csk (-h | --help)
    compass_display_csk --version

Options:
    FILENAME           CSK file containing the compass data
    --no-w-cor         Toggle off weight aligment with Z axis for calibrated data
    --csv-calib FNAME  Export csv calibrated results in FNAME
    --csv-raw FNAME    Export csv raw results in FNAME
    -h --help          Show this screen.

Example:
    compass_display_csk <filename>

"""

from docopt import docopt
import km3compass as kc
import matplotlib.pyplot as plt
import pandas as pd


def display_csk(
    filename="", weight_aligment=True, calib_csv_export=None, raw_csv_export=None
):
    """
    Display raw and calibrated measurements from CSK file





    """
    reader = kc.readerCSK(filename)
    df = None
    kc.plot_raw_results(reader.df, title="Raw data")
    if isinstance(raw_csv_export, str):
        print("Export raw measurement to csv file : {}".format(raw_csv_export))
        reader.df.set_index("datetime").to_csv(raw_csv_export)
    print()
    for modID in reader.module_IDs:
        print("-" * 10 + " Process module {} ".format(modID) + "-" * 10)
        calib = kc.calib_DB(reader, modID)
        if weight_aligment:
            calib.df = kc.align_z2weight(calib.df)
        df = pd.concat((df, calib.df))
        print()

    kc.plot_raw_results(df, title="After calibration and weight aligment")
    if isinstance(calib_csv_export, str):
        print("Export calibrated measurement to csv file : {}".format(calib_csv_export))
        df.set_index("datetime").to_csv(calib_csv_export)


def cli_display_csk():
    args = docopt(__doc__, version=kc.version)
    formated_args = dict(
        filename=args["FILENAME"],
        weight_aligment=args["--no-w-cor"] == False,
        calib_csv_export=args["--csv-calib"],
        raw_csv_export=args["--csv-raw"],
    )

    display_csk(**formated_args)
    plt.show()
