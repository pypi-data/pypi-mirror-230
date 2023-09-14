#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import km3compass as kc
import numpy as np
import matplotlib.pyplot as plt


class test_summary_plot(unittest.TestCase):
    def setUp(self):
        self.reader = kc.readerCSK("tests/DOM_0801.csk")

    def test_plot_raw_results(self):
        fig = kc.plot_raw_results(self.reader.df)
        assert isinstance(fig, plt.Figure)

    def test_append_AHRS(self):
        kc.append_AHRS(self.reader.df)

    def test_append_spherical(self):
        kc.append_spherical(self.reader.df)


class test_data_manipulation_tools(unittest.TestCase):
    def setUp(self):
        self.reader = kc.readerOnline("D_ORCA006", minrun=9000, maxrun=9000)

    def test_resampling(self):
        df = kc.resample_df(self.reader.df, period="20min")
        # 10 min run, should 1 per DOM after resampling
        assert len(self.reader.df["DOMID"].unique()) == df.shape[0]

    def test_moving_average(self):
        df = self.reader.df
        for mod in df["DOMID"].unique():
            df_loc = df[df["DOMID"] == mod]
            a = df_loc["AHRS_H0"].values
            a_new = kc.moving_average(a)
            mean_new = a_new[5]
            mean_manual = np.mean(np.concatenate((a[:5], a[6:11])))

            if np.isnan(mean_new):
                continue
            # Need to put a threshold due to different type conversion
            assert np.abs(mean_new - mean_manual) < 1e-8
