from dotenv import load_dotenv

from news_trader.handlers.figi import FigiAPI
from news_trader.handlers.lemon import LemonMarketsAPI
from news_trader.handlers.marketwatchapi import MarketWatchAPI

from news_trader.headlines import HeadLines
from news_trader.helpers import Helpers

load_dotenv()


def main():
    lemon_api: LemonMarketsAPI = LemonMarketsAPI()
    figi_api: FigiAPI = FigiAPI()
    market_watch_api: MarketWatchAPI = MarketWatchAPI()
    helpers: Helpers = Helpers(lemon_api)

    # COMMENT FROM HERE...
    headlines: HeadLines = market_watch_api.get_headlines()

    headlines.sentiment_analysis()
    headlines.aggregate_scores()

    gm_tickers = figi_api.find_gm_tickers(headlines.get_tickers())
    headlines.set_gm_tickers(gm_tickers)

    headlines.raw_dataframe.to_csv("tickers_scores.csv")
    # ...UP TO THIS POINT TO USE SAVED DATA

    # uncomment lines below and comment all tagged lines above to use saved data
    # import pandas as pd
    # headlines = HeadLines(pd.read_csv("tickers_scores.csv"))
    helpers.get_isins(headlines)

    print(f"The highest sentiment score is: {headlines.max_score}")
    print(f"The lowest sentiment score is {headlines.min_score}")

    buy, sell = headlines.get_trade_decisions()
    orders = helpers.place_trades(buy, sell)
    helpers.activate_order(orders)


if __name__ == "__main__":
    main()
