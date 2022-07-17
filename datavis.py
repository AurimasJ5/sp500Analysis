import pandas as pd
import streamlit as st
import plotly.express as px
import datetime
import sqlalchemy
import yfinance as yf

st.set_page_config(page_icon=":bar_chart:", page_title="S&P500 Analysis", layout="wide")
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

class stocks_tickers:
    def get_tickers():
        get_tickers = pd.read_html(
        "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0][["Symbol", "GICS Sector"]]
        get_tickers["Symbol"] = get_tickers["Symbol"].str.replace(".","-", regex=True)
        return get_tickers
    
    def tickers_list(get_tickers):
        return get_tickers["Symbol"].to_list()

class time_period:
    def date_now():
        return datetime.datetime.now()

    def crisis_start(y=2007, m=6, d=1):
        return datetime.datetime(y, m, d)

    def crisis_end(y=2009, m=6, d=1):
        return datetime.datetime(y, m, d)

    def corona_start(y=2019, m=12, d=1):
        return datetime.datetime(y, m, d)

    def corona_end(y=2022, m=1, d=1):
        return datetime.datetime(y, m, d)

    def ukraine_invasion_start(y=2022, m=2, d=1):
        return datetime.datetime(y, m, d)

class plots:
    def cum_return_stocks(table, con, top_tickers=None, t1=None, t2=None):
        stocks = pd.read_sql(table, con)
        stocks.set_index("Date", inplace=True)
        stocks = stocks.loc[t1:t2]
        df_daily_returns = stocks.pct_change()
        df_daily_returns = df_daily_returns[1:]
        df_cum_daily_returns = (1 + df_daily_returns).cumprod() - 1
        df_cum_daily_returns = df_cum_daily_returns.iloc[-1]
        df_cum_daily_returns.sort_values(ascending=False, inplace=True)
        tickers = df_cum_daily_returns.index[:top_tickers]
        stocks = stocks.drop(stocks.columns.difference(tickers), axis=1)
        df_daily_returns = stocks.pct_change()
        df_daily_returns = df_daily_returns[1:]
        df_cum_daily_returns = (1 + df_daily_returns).cumprod() - 1
        df_cum_daily_returns = df_cum_daily_returns.reset_index()
        df2 = df_cum_daily_returns.melt(id_vars=["Date"], var_name="ticker", value_name="cum_return")
        df2["cum_return_pct"] = df2["cum_return"] * 100
        fig = px.line(df2, x="Date",
              y="cum_return_pct", color="ticker",
              labels={"cum_return_pct":"daily cumulative returns (%)", }
            )
        fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.05 ,xanchor="left", x=0)
            )
        return fig

    def cum_return_sectors(table, con, t1=None, t2=None):
        stocks = pd.read_sql(table, con)
        stocks.set_index("Date", inplace=True)
        stocks = stocks.loc[t1:t2]
        stocks.reset_index(inplace=True)
        stocks = stocks.melt(id_vars="Date", var_name="Tickers", value_name="Price")
        tickers = stocks_tickers.get_tickers()
        stocks = pd.merge(stocks, tickers, left_on="Tickers", right_on="Symbol")
        stocks.drop(["Symbol", "Tickers"], axis=1, inplace=True)
        df = stocks.pivot_table(index=["Date"], columns="GICS Sector", values=["Price"])
        df.columns = [col[1] for col in df.columns.values]
        df_daily_returns = df.pct_change()
        df_daily_returns = df_daily_returns[1:]
        df_cum_daily_returns = (1 + df_daily_returns).cumprod() - 1
        df_cum_daily_returns = df_cum_daily_returns.reset_index()
        df2 = df_cum_daily_returns.melt(
            id_vars=["Date"], var_name="Sector", value_name="cum_return")
        df2["cum_return_pct"] = df2["cum_return"] * 100
        fig = px.line(
            df2, x="Date", y="cum_return_pct", color="Sector",
            labels={"cum_return_pct":"daily cumulative returns (%)", }
            )
        fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.05 ,xanchor="left", x=0)
            )
        return fig

    def top_holders_pie(table1, table2, con, top=10):
        holder_df = pd.read_sql(table1, con)
        market_cap_df = pd.read_sql(table2, con)
        market_cap_sp500 = market_cap_df["MarketCap"].sum()
        holder_df_top10 = holder_df[:top]
        holder_df_top10.drop(holder_df_top10.columns.difference(["Holders", "Assets"]), axis=1, inplace=True)
        holder_df_top10.at[top, "Assets"] = market_cap_sp500 - holder_df_top10["Assets"].sum()
        holder_df_top10.at[top, "Holders"] = "S&P500"
        fig = px.pie(
            holder_df_top10, values="Assets", names="Holders", hole=0.6
            )
        return fig

    def top_market_cap_pie(table, con, top=10):
        market_cap_df = pd.read_sql(table, con)
        market_cap_sp500 = market_cap_df["MarketCap"].sum()
        market_cap_df_top10 = market_cap_df[:top]
        market_cap_df_top10.drop(
        market_cap_df_top10.columns.difference(["Ticker", "MarketCap"]), axis=1, inplace=True
            )
        market_cap_df_top10.at[top, "MarketCap"] = market_cap_sp500 - market_cap_df_top10["MarketCap"].sum()
        market_cap_df_top10.at[top, "Ticker"] = "S&P500"
        fig = px.pie(
            market_cap_df_top10, values="MarketCap", names="Ticker", hole=0.6
            )
        fig.update_traces(textinfo="label+percent")
        return fig

    def sp500_historical_data(tickers, t1, t2):
        SP500 = yf.download(tickers, t1, t2)["Close"]
        df_daily_returns = SP500.pct_change()
        df_daily_returns = df_daily_returns[1:]
        df_cum_daily_returns = (1 + df_daily_returns).cumprod() - 1
        return df_cum_daily_returns

engine = sqlalchemy.create_engine("sqlite:///data.db")

tickers = stocks_tickers.get_tickers()
tickers_list = stocks_tickers.tickers_list(tickers)

st.title("S&P500 Analysis")
st.subheader("Check stocks data visualization of this century with the timestamp of more than 20 years")

col1, col2 = st.columns(2)

with col1:
    st.markdown("Top 3 stock exchanges performance")
    fig = plots.cum_return_stocks(table="stock_exchange_top", con=engine)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.write("Top 10 stocks performance")
    fig = plots.cum_return_stocks(table="sp500", con=engine, top_tickers=10)
    st.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.write("How sectors are changing based on stocks performance") 
    fig = plots.cum_return_sectors(table="sp500", con=engine)
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.write("Top 10 stocks performance during Financial Crisis 2008") 
    fig = plots.cum_return_stocks(table="sp500", con=engine, top_tickers=10,
        t1=str(time_period.crisis_start()), t2=str(time_period.crisis_end())
        ) 
    st.plotly_chart(fig, use_container_width=True)

col5, col6 = st.columns(2)

with col5:
    st.write("Top 10 stocks performance during Corona Virus") 
    fig = plots.cum_return_stocks(table="sp500", con=engine, top_tickers=10,
        t1=str(time_period.corona_start()), t2=str(time_period.corona_end())
        )  
    st.plotly_chart(fig, use_container_width=True)

with col6:
    st.write("Top 10 stocks performance during Russian invasion of Ukraine")
    fig = plots.cum_return_stocks(table="sp500", con=engine, top_tickers=10,
        t1=str(time_period.ukraine_invasion_start()), t2=str(time_period.date_now())
        ) 
    st.plotly_chart(fig, use_container_width=True)

col7, col8 = st.columns(2)

with col7:
    st.write("Top 10 Holders in comparison with the rest of S&P 500 market") 
    fig = plots.top_holders_pie(table1="top_holders", 
        table2="sp500_market_cap", con=engine) 
    st.plotly_chart(fig, use_container_width=True)

with col8:
    st.write("Top 10 stocks with highest market cap") 
    fig = plots.top_market_cap_pie(table="sp500_market_cap", con=engine)
    st.plotly_chart(fig, use_container_width=True)

st.header("Check Individual Stocks:")

dropdown = st.multiselect("Select one or multiple stocks", tickers_list)

start = st.date_input("Start Date", value = pd.to_datetime("2022-01-01"))
end = st.date_input("End Date", value = pd.to_datetime("today"))

if len(dropdown) > 0:
    st.header("{} growth over selected period".format(dropdown))
    st.line_chart(plots.sp500_historical_data(tickers=dropdown, t1=start, t2=end))