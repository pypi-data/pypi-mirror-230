#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import km3compass as kc
import pandas as pd


class test_calib(unittest.TestCase):
    def setUp(self):
        self.reader = kc.readerCSK("tests/DOM_0801.csk")
        self.calib = kc.calib_DB(self.reader, 817302522, calibrate=True)
        self.accept = kc.acceptance_test(self.calib, 817302522)

    def test_results(self):
        assert "card [deg]" in self.accept.df_merged.columns
        assert "residual [deg]" in self.accept.df_merged.columns
        assert "yaw" in self.accept.residuals
        assert "module ID" in self.accept.residuals
        assert "res 0" in self.accept.residuals
        assert "res 1" in self.accept.residuals
        assert "res 2" in self.accept.residuals
        assert "res 3" in self.accept.residuals

    def test_plot(self):
        self.accept.plot_results()
