#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import km3compass as kc
import pandas as pd


class test_reader_CSK(unittest.TestCase):
    def setUp(self):
        self.reader = kc.readerCSK("tests/DOM_0801.csk")

    def test_df(self):
        df = self.reader.df
        assert isinstance(df, pd.DataFrame)

    def test_df_content(self):
        df = self.reader.df
        col_to_check = [
            "AHRS_A0",
            "AHRS_A1",
            "AHRS_A2",
            "AHRS_H0",
            "AHRS_H1",
            "AHRS_H2",
            "time",
            "DOMID",
        ]
        for col in col_to_check:
            assert col in df.columns
