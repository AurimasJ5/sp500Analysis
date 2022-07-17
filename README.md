# About The Project
2000-01-01 was picked as the project's starting date to precisely accumulate this centuries historical data of 
S&P 500 stock exchange market, which has 500 leading publicly traded companies in the U.S .

### The project includes:
- Top 3 stock exchanges performance
- Top 10 stocks performance
- How sectors are changing based on stocks performance
- Top 10 stocks performance during Financial Crisis 2008
- Top 10 stocks performance during Corona Virus
- Top 10 stocks performance during Russian invasion of Ukraine
- Top 10 Holders in comparison with the rest of S&P 500 market
- Top 10 stocks with highest market cap
- Check growth of individual stock or multiple stocks 

# Getting Started
With a help of SQLITE data.db file is created holding data till 2022-07-13 .
To get top holders and top market cap data , it can take a few hours in comparison to get only prices - just a few
minutes. If top holders and top market cap methods aren't necessary, I would strongly recommend to comment out them.
- To update data: <br />
run getdata.py file or use terminal `python3 run getdata.py`
- To run project: <br />
`streamlit run datavis.py`

# Note
- To get best experience slide mouse onto graph, then additional options pops up, use **View fullscreen mode.**<br />
- Zoom in by clicking onto graph and dragging to needed timestamp.
