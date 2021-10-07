from typing import List

from dotenv import load_dotenv

import pandas as pd
import datetime

from news_trader.handlers.figi import FIGI
from news_trader.handlers.lemon import LemonMarketsAPI
from news_trader.handlers.marketwatch import MarketWatch

# set options to display all columns and rows when printing dataframes
from news_trader.headlines import HeadLines

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

lemon_api = LemonMarketsAPI()
figi = FIGI()
market_watch = MarketWatch()


def get_isins(headlines: HeadLines):
    isins = []

    for ticker in headlines.get_gm_tickers():
        if ticker == "NA":
            isins.append("NA")

        else:
            try:
                instrument = lemon_api.get_instrument(ticker)

                if instrument.get("count") > 0:
                    isins.append(instrument.get("results")[0].get("isin"))
                else:
                    isins.append("NA")

            except Exception as e:
                print(e)

    headlines.set_isins(isins)


def trade_decision(dataframe: pd.DataFrame):
    buy = []
    sell = []
    for index, row in dataframe.iterrows():
        # if sentiment higher than 0.5 and ISIN present, place ISIN in buy list
        if row["score"] > 0.5 and row["isin"] != "NA":
            print(
                f'Buy {row["ticker"]} ({row["isin"]}) with sentiment score {row["score"]}.'
            )
            buy.append(row["isin"])
        # if sentiment lower than -0.5 and ISIN present, place ISIN in sell list
        if row["score"] < -0.5 and row["isin"] != "NA":
            print(
                f'Sell {row["ticker"]} ({row["isin"]}) with sentiment score {row["score"]}.'
            )
            sell.append(row["isin"])

    return buy, sell


def place_trades(buy: List[str], sell: List[str]):
    orders = []

    space_uuid = lemon_api.get_space_uuid()
    valid_time = (datetime.datetime.now() + datetime.timedelta(hours=1)).timestamp()

    # place buy orders
    for isin in buy:
        side = "buy"
        quantity = 1
        order = lemon_api.place_order(isin, valid_time, quantity, side, space_uuid)
        orders.append(order)
        print(f"You are {side}ing {quantity} share(s) of instrument {isin}.")

    portfolio = lemon_api.get_portfolio(space_uuid)

    # place sell orders
    for isin in sell:
        if isin in portfolio:
            side = "sell"
            quantity = 1
            order = lemon_api.place_order(isin, valid_time, quantity, side, space_uuid)
            orders.append(order)
            print(f"You are {side}ing {quantity} share(s) of instrument {isin}.")
        else:
            print(
                f"You do not have sufficient holdings of instrument {isin} to place a sell order."
            )

    return orders


def activate_order(orders):
    for order in orders:
        lemon_api.activate_order(order.get("uuid"), lemon_api.get_space_uuid())
        print(f'Activated {order.get("isin")}')
    return orders


def main():
    headlines: HeadLines = market_watch.get_headlines()

    headlines.remove_tickers(REMOVABLE_TICKERS)
    headlines.sentiment_analysis()
    headlines.aggregate_scores()

    tickers = headlines.get_tickers()
    gm_tickers = figi.find_gm_tickers(tickers)

    headlines.set_gm_tickers(gm_tickers)
    headlines.save()

    # uncomment this and comment all lines from scrape_data() function to find_gm_tickers() function in main() to use saved data
    # headlines = HeadLines(pd.read_csv("tickers_scores.csv"))

    get_isins(headlines)

    print(f"The highest sentiment score is: {headlines.max_score}")
    print(f"The lowest sentiment score is {headlines.min_score}")

    buy, sell = headlines.get_trade_decisions()
    orders = place_trades(buy, sell)
    activate_order(orders)


if __name__ == "__main__":
    main()
