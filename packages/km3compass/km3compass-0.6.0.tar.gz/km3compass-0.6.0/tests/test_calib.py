#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import km3compass as kc
import pandas as pd


class test_agent_DB(unittest.TestCase):
    def setUp(self):
        self.agent = kc.calibration_DB_agent()

    def test_get_CLB_UPI(self):
        upi = self.agent.get_CLB_UPI("08:00:30:38:57:33")
        assert upi == "3.4.3.2/V2-2-1/2.195"

    def test_get_compass_UPI(self):
        upi = self.agent.get_compass_UPI("3.4.3.2/V2-2-1/2.195")
        assert upi == "3.4.3.4/LSM303/2.195"

    def test_get_compass_UPI(self):
        calibration = self.agent.get_calibration(195)
        assert isinstance(calibration, kc.calibration_object)


class test_calibration_object(unittest.TestCase):
    def setUp(self):
        self.calibration = kc.calibration_object(moduleID=0)

    def test_export_json(self):
        self.calibration.to_json("test_calib.json")

    def test_export_jpp(self):
        self.calibration.to_jpp("test_calib_jpp.txt")


class test_calib_DB(unittest.TestCase):
    def setUp(self):
        self.reader = kc.readerCSK("tests/DOM_0801.csk")
        self.calib = kc.calib_DB(self.reader, 817302522, calibrate=True)

    def test_calibration_results(self):
        assert isinstance(self.calib.calibration, kc.calibration_object)

    def test_calibration_print(self):
        assert isinstance(self.calib.print_calibration(), type(None))


class test_calib_self_sphere(unittest.TestCase):
    def setUp(self):
        self.reader = kc.readerCSK("tests/DOM_0801.csk")
        self.calib = kc.calib_self_sphere(self.reader, 817302522)

    def test_calibration_results(self):
        assert hasattr(self.calib, "center")
        assert hasattr(self.calib, "radius")

    def test_calibration_plot(self):
        assert isinstance(self.calib.plot_results(), type(None))


class test_detector_calibration(unittest.TestCase):
    def setUp(self):
        self.detoid = "D_ORCA006"
        self.reader = kc.readerOnline(self.detoid, minrun=9000, maxrun=9000)
        self.calib = kc.detector_calibration(self.reader)
        self.calib.apply_calibration()

    def test_calibration(self):
        self.calib.print_calibration_summary()
        self.calib.plot_calibration_summary()


class test_calib_ellipsoid_fit(unittest.TestCase):
    def setUp(self):
        self.reader = kc.readerCSK("tests/compass_3_1101_calibration.csk")
        self.calib = kc.calibration_ellipsoid_fit(self.reader)

    def test_calibration_results(self):
        assert isinstance(self.calib.get_calibration(), kc.calibration_object)
