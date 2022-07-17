import pandas as pd
import yfinance as yf
import sqlalchemy
import datetime
import time

class stocks_tickers:
    def get_tickers():
        get_tickers = pd.read_html(
        "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0][["Symbol", "GICS Sector"]]
        get_tickers["Symbol"] = get_tickers["Symbol"].str.replace(".","-", regex=True)
        return get_tickers
    
    def tickers_list(get_tickers):
        return get_tickers["Symbol"].to_list()

class time_period:
    def start_date(y, m, d):
        return datetime.datetime(y, m, d)

    def date_now():
        return datetime.datetime.now()

class stock_exchanges_top3:
    def top3_historical_data(t1, t2):
        stock_exchange_top = yf.download(["^GSPC", "^IXIC", "^DJI"], t1, t2)["Close"]
        stock_exchange_top.rename(columns={
        "^GSPC" : "NASDAQ",
        "^IXIC" : "S&P500",
        "^DJI" : "Dow Jones Industrial Average"
        }, inplace = True)
        return stock_exchange_top

class sp500:
    def sp500_historical_data(tickers, t1, t2):
        SP500 = yf.download(tickers, t1, t2)["Close"]
        SP500.columns = SP500.columns.str.replace(".","-", regex=True)
        return SP500

class sp500_market_cap():
    def market_cap():
        market_cap = {}

        get_tickers = stocks_tickers.get_tickers()
        tickers = stocks_tickers.tickers_list(get_tickers=get_tickers)
        for ticker in tickers:
            try:
                i = yf.Ticker(ticker)
                i = i.get_info()["marketCap"]
                market_cap[ticker] = i
            except TypeError:
                pass
            except KeyError:
                pass
            except ConnectionError:
                time.sleep(5)
                pass 
        return market_cap

    def ticker_keys(market_cap):
        return list(market_cap.keys())

    def market_cap_values(market_cap):
        return list(market_cap.values())

    def market_cap_df(ticker_keys, market_cap_values):
        return pd.DataFrame({
        "Ticker" : ticker_keys,
        "MarketCap" : market_cap_values
        })

    def get_none_tickers_list(market_cap_df):
        return market_cap_df["Ticker"][market_cap_df["MarketCap"].isnull()].tolist()

    def get_none_index_list(market_cap_df):
        return market_cap_df["Ticker"][market_cap_df["MarketCap"].isnull()].index.values.tolist()

    def update_market_cap(market_cap_df, tickers, index):
        update_market_cap = []
        for ticker in tickers:
            try:
                i = yf.Ticker(ticker)
                i = i.get_info()["marketCap"]
                update_market_cap.append(i)
            except TypeError:
                break
            except KeyError:
                pass
            except ConnectionError:
                break
        for ticker, value in zip(index, update_market_cap):
            try:
                market_cap_df.at[ticker, "MarketCap"] = value
            except TypeError:
                break
        return market_cap_df

class sp500_top_holders:
    def top_holders(tickers, SP500):
        top_holders = {}

        for symbol in tickers:
            try:
                holders_assets_pair = yf.Ticker(symbol).get_institutional_holders()[["Holder", "Shares"]]
                holders_assets_pair.drop_duplicates(keep="first", inplace=True)
                holders = holders_assets_pair["Holder"].to_list()
                assets = holders_assets_pair["Shares"].to_list()
                ticker_latest_price = float(SP500[symbol][-1])
                for holder, asset in zip(holders, assets):
                    if asset is None:
                        pass
                    elif str(holder) not in top_holders:
                        top_holders[str(holder)] = float(asset)*ticker_latest_price
                    else:
                        top_holders[str(holder)] = top_holders[str(holder)] + float(asset)*ticker_latest_price
            except TypeError:
                pass
            except KeyError:
                pass
            except ConnectionError:
                time.sleep(5)
                pass
        return top_holders

    def holder_keys(top_holders):
        return list(top_holders.keys())

    def holder_values(top_holders):
        return list(top_holders.values())

    def top_holders_df(holder_keys, holder_values):
        return pd.DataFrame({
            "Holders" : holder_keys,
            "Assets" : holder_values
            })

engine = sqlalchemy.create_engine("sqlite:///data.db")

tickers = stocks_tickers.get_tickers()
tickers_list = stocks_tickers.tickers_list(tickers)

start_date = time_period.start_date(y=2000, m=1, d=1)
now = time_period.date_now()

top3_stock_exchanges = stock_exchanges_top3.top3_historical_data(t1=start_date, t2=now)
top3_stock_exchanges.to_sql("stock_exchange_top", engine, if_exists="replace")

SP500 = sp500.sp500_historical_data(tickers=tickers_list, t1=start_date, t2=now)
SP500.to_sql("sp500", engine, if_exists="replace")

# Get top holders
SP500 = pd.read_sql("sp500", engine, index_col="Date")
top_holders = sp500_top_holders.top_holders(SP500=SP500, tickers=tickers_list)
holder_keys = sp500_top_holders.holder_keys(top_holders=top_holders)
holder_values = sp500_top_holders.holder_values(top_holders=top_holders)
top_holders_df = sp500_top_holders.top_holders_df(
    holder_keys=holder_keys,
    holder_values=holder_values
    )   
top_holders_df.sort_values(by="Assets", ascending=False, inplace=True)
top_holders_df.to_sql("top_holders", engine, if_exists="replace", index=False)

# Get market cap
market_cap = sp500_market_cap.market_cap()
ticker_keys = sp500_market_cap.ticker_keys(market_cap=market_cap)
market_values = sp500_market_cap.market_cap_values(market_cap=market_cap)
market_cap_df = sp500_market_cap.market_cap_df(
    market_cap_values=market_values,
    ticker_keys=ticker_keys
    )
tickers = sp500_market_cap.get_none_tickers_list(market_cap_df=market_cap_df)
index = sp500_market_cap.get_none_index_list(market_cap_df=market_cap_df)
market_cap_df = sp500_market_cap.update_market_cap(
    market_cap_df=market_cap_df,
    tickers=tickers,
    index=index
    )
market_cap_df.sort_values(by="MarketCap", ascending=False, inplace=True)
market_cap_df.to_sql("sp500_market_cap", engine, if_exists="replace", index=False)

