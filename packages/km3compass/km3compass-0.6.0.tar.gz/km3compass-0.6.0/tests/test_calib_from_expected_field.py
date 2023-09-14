#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import km3compass as kc
import pandas as pd


class calib_from_expected_field(unittest.TestCase):
    def setUp(self):
        self.reader = kc.readerOnline("D_ORCA006", minrun=9000, maxrun=9000)
        test_domid = self.reader.df["DOMID"].iloc[0]
        self.calib = kc.calib_from_expected_field(self.reader, test_domid)

    def test_calib_class(self):
        assert hasattr(self.calib, "center")
        assert hasattr(self.calib, "radius")
        assert hasattr(self.calib, "calibration")
