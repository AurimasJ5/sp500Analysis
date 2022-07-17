import unittest
from datavis import *
import pandas as pd
from datetime import datetime

class Test_datavis(unittest.TestCase):
    def setUp(self):
        self.get_tickers = stocks_tickers.get_tickers()
        self.tickers_list = stocks_tickers.tickers_list(self.get_tickers)

    def test_get_tickers(self):
        self.assertIsNotNone(self.get_tickers)
        self.assertIsInstance(self.get_tickers, pd.DataFrame)

    def test_tickers_list(self):
        self.assertIsInstance(self.tickers_list, list)

    def test_crisis_start(self):
        self.assertEqual(time_period.crisis_start(), datetime(2007, 6, 1))

    def test_crisis_end(self):
        self.assertEqual(time_period.crisis_end(), datetime(2009, 6, 1))       
    
    def test_corona_start(self):
        self.assertEqual(time_period.corona_start(), datetime(2019, 12, 1))  

    def test_corona_end(self):
        self.assertEqual(time_period.corona_end(), datetime(2022, 1, 1)) 

    def test_invasion_start(self):
        self.assertEqual(time_period.ukraine_invasion_start(), datetime(2022, 2, 1)) 

    def test_historical_data(self):
        sp500 = plots.sp500_historical_data("GOOG", "2022-02-04", "2022-02-06")
        self.assertIsNotNone(sp500)
        self.assertIsInstance(sp500, pd.Series)
        sp500_2 = plots.sp500_historical_data(["GOOG", "TSLA", "MMM"], "2022-03-04", "2022-03-10")
        self.assertIsNotNone(sp500_2)
        self.assertIsInstance(sp500_2, pd.DataFrame)

if __name__ == "__main__":
    unittest.main()