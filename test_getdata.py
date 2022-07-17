import unittest
from getdata import *
from datetime import datetime
import pandas as pd
import random

class Test_getdata(unittest.TestCase):
    def setUp(self):
        self.get_tickers = stocks_tickers.get_tickers()
        self.tickers_list = stocks_tickers.tickers_list(self.get_tickers)
        self.sp500_market_cap = sp500_market_cap.market_cap()
        self.sp500_market_cap_values = sp500_market_cap.market_cap_values(sp500_market_cap.market_cap())
        self.sp500_market_cap_keys = sp500_market_cap.ticker_keys(sp500_market_cap.market_cap())
        self.market_cap_df = sp500_market_cap.market_cap_df(
            ticker_keys=self.sp500_market_cap_keys,
            market_cap_values=self.sp500_market_cap_values
            )
        self.top_holders = sp500_top_holders.top_holders(
            tickers=self.tickers_list, 
            SP500=pd.read_sql("sp500", engine, index_col="Date")
            )
        self.top_holders_keys = sp500_top_holders.holder_keys(self.top_holders)
        self.top_holders_values = sp500_top_holders.holder_values(self.top_holders)
        self.top_holders_df = sp500_top_holders.top_holders_df(
            holder_keys=self.top_holders_keys,
            holder_values=self.top_holders_values
            )

    def test_get_tickers(self):
        self.assertIsNotNone(self.get_tickers)
        self.assertIsInstance(self.get_tickers, pd.DataFrame)

    def test_tickers_list(self):
        self.assertIsNotNone(self.tickers_list)
        self.assertIsInstance(self.tickers_list, list)

    def test_start_date(self):
        self.assertEqual(time_period.start_date(2020, 5, 5), datetime(2020, 5, 5))

    def test_stock_exchanges(self):
        stock_exchanges = stock_exchanges_top3.top3_historical_data(t1="2022-01-04", t2="2022-02-06")
        self.assertIsNotNone(stock_exchanges)
        self.assertIsInstance(stock_exchanges, pd.DataFrame)

    def test_stock_exchanges(self):
        sp500_1 = sp500.sp500_historical_data("GOOG", "2022-02-04", "2022-02-08")
        self.assertIsNotNone(sp500_1)
        self.assertIsInstance(sp500_1, pd.Series)
        sp500_2 = sp500.sp500_historical_data(["GOOG", "TSLA", "MMM"], "2022-03-04", "2022-03-10")
        self.assertIsNotNone(sp500_2)
        self.assertIsInstance(sp500_2, pd.DataFrame)

    def test_market_cap(self):
        self.assertIsNotNone(self.sp500_market_cap)
        self.assertIn(random.choice(self.tickers_list), self.sp500_market_cap.keys)

    def test_ticker_keys(self):
        self.assertIsNotNone(self.sp500_market_cap_keys)
        self.assertIsInstance(self.sp500_market_cap_keys, list)

    def test_market_cap_values(self):
        self.assertIsNotNone(self.sp500_market_cap_values)
        self.assertIsInstance(self.sp500_market_cap_values, list)

    def test_market_cap_df(self):
        self.assertIsNotNone(self.market_cap_df)
        self.assertIsInstance(self.market_cap_df, pd.DataFrame)

    def test_top_holders(self):
        self.assertIsNotNone(self.top_holders)

    def test_top_holders_keys(self):
        self.assertIsNotNone(self.top_holders_keys)
        self.assertIsInstance(self.top_holders_keys, list)

    def test_top_holders_values(self):
        self.assertIsNotNone(self.top_holders_values)
        self.assertIsInstance(self.top_holders_values, list)

    def test_top_holders_df(self):
        self.assertIsNotNone(self.top_holders_df)
        self.assertIsInstance(self.top_holders_df, pd.DataFrame)

if __name__ == "__main__":
    unittest.main()