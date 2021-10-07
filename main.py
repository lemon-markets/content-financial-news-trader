from dotenv import load_dotenv

import pandas as pd

from news_trader.handlers.figi import FIGI
from news_trader.handlers.lemon import LemonMarketsAPI
from news_trader.handlers.marketwatch import MarketWatch

# set options to display all columns and rows when printing dataframes
from news_trader.headlines import HeadLines
from news_trader.helpers import Helpers

pd.options.display.max_columns = None
pd.options.display.max_rows = None

# pre-emptively decide on some tickers to exclude to make dataset smaller
REMOVABLE_TICKERS = [
    "SPX",
    "DJIA",
    "BTCUSD",
    "",
    "GCZ21",
    "HK:3333",
    "DX:DAX",
    "XE:VOW",
    "UK:AZN",
    "GBPUSD",
    "CA:WEED",
    "UK:UKX",
    "CA:ACB",
    "CA:ACB",
    "CA:CL",
    "BX:TMUBMUSD10Y",
]

load_dotenv()


def main():
    lemon_api: LemonMarketsAPI = LemonMarketsAPI()
    figi_api: FIGI = FIGI()
    market_watch_api: MarketWatch = MarketWatch()

    headlines: HeadLines = market_watch_api.get_headlines()
    helpers: Helpers = Helpers(lemon_api)

    headlines.remove_tickers(REMOVABLE_TICKERS)
    headlines.sentiment_analysis()
    headlines.aggregate_scores()

    tickers = headlines.get_tickers()

    gm_tickers = figi_api.find_gm_tickers(tickers)

    headlines.set_gm_tickers(gm_tickers)
    headlines.raw_dataframe.to_csv("tickers_scores.csv")

    # uncomment this and comment all lines from scrape_data() function to find_gm_tickers() function in main() to use saved data
    # headlines = HeadLines(pd.read_csv("tickers_scores.csv"))
    helpers.get_isins(headlines)

    print(f"The highest sentiment score is: {headlines.max_score}")
    print(f"The lowest sentiment score is {headlines.min_score}")

    buy, sell = headlines.get_trade_decisions()
    orders = helpers.place_trades(buy, sell)
    helpers.activate_order(orders)


if __name__ == "__main__":
    main()
