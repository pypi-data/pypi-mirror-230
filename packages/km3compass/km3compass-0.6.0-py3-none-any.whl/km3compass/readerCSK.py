#!/usr/bin/env python3
from .tools import load_CSK, cart2spherical

import pandas as pd
import numpy as np


class readerCSK:
    """
    Reader to load CSK data

    Parameters:
    -----------
    filename: str
      Path to CSK file
    remove_duplicates: bool, default=True
      Toggle duplicated measurement filter
    """

    def __init__(self, filename, remove_duplicates=True):
        self.filename = filename
        self.rawframe = load_CSK(self.filename)
        self.df = pd.DataFrame(self.rawframe)
        self.df["datetime"] = pd.to_datetime(self.df["time"], unit="s").fillna(pd.NaT)
        # Print some generic informations about the file
        print("File loaded, {} rows".format(self.df.shape[0]))
        self.module_IDs = np.unique(self.df["DOMID"])
        print("\t{} module(s)".format(len(self.module_IDs)))
        for mod in self.module_IDs:
            print("\t- {}".format(mod))

        if remove_duplicates:
            # filter DF to remove duplicated values
            self.df = self.df.drop_duplicates(
                subset=[
                    "AHRS_A0",
                    "AHRS_A1",
                    "AHRS_A2",
                    "AHRS_H0",
                    "AHRS_H1",
                    "AHRS_H2",
                    "DOMID",
                ]
            )
            print(
                "Number of measurements after removing duplicates : {}".format(
                    self.df.shape[0]
                )
            )
