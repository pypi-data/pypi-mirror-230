#!/usr/bin/env python3
from .tools import cart2spherical

import pandas as pd
import numpy as np
import km3db
import sys


class readerOnline:
    """
    Reader to load online (sea) data

    Parameters:
    -----------
    detoid: str
      Detector name, e.g. D_ORCA006 for ORCA6
    minrun: int
      Minimum run number
    maxrun: int
      Maximum run number (included)
    filename: str
      filename to load data. If specified, will load from file instead of DB
    filenkey: str
      Key inside the file. Mandatory if loading from file.
    """

    def __init__(
        self,
        detoid="D_ORCA006",
        minrun=9001,
        maxrun=9010,
        filename="",
        filekey="",
        kwargs_query={},
    ):
        self.sds = km3db.StreamDS(container="pd")
        self.detoid = detoid
        self.runs = [minrun, maxrun]
        self.kwargs_query = kwargs_query
        self.df = None

        if filename != "":
            self.load_df(filename, filekey)

        else:
            self.load_from_DB()

        self.module_IDs = np.unique(self.df["DOMID"])

    def save_df(self, filename, df_name=""):
        """
        Save loaded data into a h5 file

        Parameters:
        -----------
        filename: str
          Path to h5 file
        df_name: str
          Key given to the dataframe inside the h5 file
        """

        if df_name == "":
            df_name = "runs_{}_{}".format(*self.runs)

        store = pd.HDFStore(filename)
        store[df_name] = self.df
        print("Data stored in '{}', under key '{}'".format(filename, df_name))

    def load_df(self, filename, df_name):
        """
        Load data from a h5 file

        Parameters:
        -----------
        filename: str
          Path to h5 file
        df_name: str
          Key given to the dataframe inside the h5 file
        """

        print("Filename provided, will load data from disk ...")
        print("\tfilename = {}\n\tfilekey =  {}".format(filename, df_name))
        store = pd.HDFStore(filename)
        self.df = store[df_name]

    def load_from_DB(self):
        """Load data from Database"""
        print("Loading data from DB ...")

        print(
            "\tdetoid = {}\n\tminrun = {}\n\tmaxrun = {}".format(
                self.detoid, *self.runs
            )
        )

        self.df = None
        nRuns = self.runs[1] - self.runs[0] + 1
        for run in np.linspace(self.runs[0], self.runs[1], nRuns, dtype=int):
            print("\tGetting run {}...".format(run), end="")
            sys.stdout.flush()
            start = np.datetime64("now")
            df = self.sds.ahrs(
                detid=self.detoid, minrun=run, maxrun=run, **self.kwargs_query
            )
            print(" - Done in {}".format(str(np.datetime64("now") - start)))
            self.df = pd.concat((self.df, df), axis=0)

        self.df.sort_values("UNIXTIME", inplace=True)
        self.df["datetime"] = pd.to_datetime(self.df["UNIXTIME"], unit="ms").fillna(
            pd.NaT
        )
