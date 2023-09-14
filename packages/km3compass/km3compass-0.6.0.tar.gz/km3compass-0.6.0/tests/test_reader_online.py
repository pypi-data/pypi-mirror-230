#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import km3compass as kc
import pandas as pd


class test_reader_Online(unittest.TestCase):
    def setUp(self):
        self.reader = kc.readerOnline("D_ORCA006", minrun=9000, maxrun=9000)

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
            "datetime",
            "DOMID",
        ]
        for col in col_to_check:
            assert col in df.columns

    def test_save_df(self):
        self.reader.save_df("test.h5", "test")
        self.reader = kc.readerOnline(filename="test.h5", filekey="test")
