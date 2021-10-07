from dotenv import load_dotenv
import requests
import pandas as pd
import datetime
import time

from bs4 import BeautifulSoup
from dateutil.parser import isoparse
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from news_trader.handlers.figi import FIGI
from news_trader.handlers.lemon import LemonMarketsAPI

load_dotenv()

lemon_api = LemonMarketsAPI()


def scrape_data(base_url: str, url_endpoints: list):
    """Scrapes headline, ticker and date from articles as presented on MarketWatch"""
    headlines = []

    for url in url_endpoints:
        page = requests.get(base_url + url)
        soup = BeautifulSoup(page.content, "html.parser")
        article_contents = soup.find_all("div", class_="article__content")

        for article in article_contents:
            # determine whether ticker present
            ticker = article.find("span", class_="ticker__symbol")

            # if ticker present in article, add both ticker and headline to list
            if ticker is not None:
                headline = article.find("a", class_="link").text.strip()
                timestamp = article.find("span", class_="article__timestamp")
                if timestamp is not None:
                    time_stamp = isoparse(timestamp["data-est"])
                # if no timestamp, assume current article and initialise timestamp to now
                else:
                    time_stamp = datetime.datetime.now()

                head_and_tick = [headline, ticker.text, time_stamp]
                headlines.append(head_and_tick)

    columns = ["headline", "ticker", "timestamp"]
    headlines_df = pd.DataFrame(headlines, columns=columns)
    print(headlines_df.head())
    return headlines_df


def filter_dataframe(dataframe, removable_tickers: list):
    filtered_dataframe = dataframe[
        ~dataframe.loc[:, "ticker"].isin(removable_tickers)
    ].copy()
    print(filtered_dataframe.head())
    return filtered_dataframe


def sentiment_analysis(dataframe):
    # initialise VADER
    try:
        vader = SentimentIntensityAnalyzer()
    except LookupError:
        import nltk

        nltk.download("vader_lexicon")
        vader = SentimentIntensityAnalyzer()

    scores = []

    # perform sentiment analysis
    for headline in dataframe.loc[:, "headline"]:
        score = vader.polarity_scores(headline).get("compound")
        scores.append(score)

    # append scores to DataFrame
    dataframe.loc[:, "score"] = scores
    print(dataframe.head())
    return dataframe


def aggregate_scores(dataframe):
    grouped_tickers = dataframe.groupby("ticker").mean()
    grouped_tickers.reset_index(level=0, inplace=True)
    print(grouped_tickers.head())
    return grouped_tickers


def find_gm_tickers(dataframe):
    print("Collecting tickers...")

    gm_tickers = []
    iteration = 1

    for ticker in dataframe.loc[:, "ticker"]:
        job = {"query": ticker, "exchCode": "GM"}
        gm_ticker = FIGI().search_jobs(job)

        # if instrument listed on GM, then collect ticker
        if gm_ticker.get("data"):
            result = gm_ticker.get("data")[0].get("ticker")
        else:
            result = "NA"

        print(f"{ticker} is {result}")
        gm_tickers.append(result)
        iteration += 1

        # OpenFIGI allows 20 requests per minute, thus sleep for 60 seconds after every 20 requests
        if iteration % 20 == 0:
            print("Sleeping for 60 seconds...")
            time.sleep(60)

    dataframe.loc[:, "gm_ticker"] = gm_tickers
    print(dataframe.head())

    return dataframe


def get_isins(dataframe):
    isins = []

    for ticker in dataframe.loc[:, "gm_ticker"]:
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

    dataframe.loc[:, "isin"] = isins
    print(dataframe)
    return dataframe


def trade_decision(dataframe):
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


def place_trades(dataframe):
    buy, sell = trade_decision(dataframe)

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
    # set options to display all columns and rows when printing dataframes
    pd.options.display.max_columns = None
    pd.options.display.max_rows = None

    # import data source
    base_url = "https://www.marketwatch.com/investing/"
    url_endpoints = [
        "barrons",
        "aerospace-defense",
        "autos",
        "biotech",
        "energy",
        "health-care",
        "media",
        "pharmaceutical",
        "retail",
        "telecommunications",
        "airlines",
        "banking",
        "food-beverage",
        "internet-online-services",
        "metals-mining",
        "real-estate-construction",
        "software",
        "technology",
    ]

    headlines = scrape_data(base_url, url_endpoints)

    # pre-emptively decide on some tickers to exclude to make dataset smaller
    removable_tickers = [
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

    headlines = filter_dataframe(headlines, removable_tickers)
    headlines = sentiment_analysis(headlines)
    headlines = aggregate_scores(headlines)
    headlines = find_gm_tickers(headlines)
    headlines.to_csv("tickers_scores.csv")

    lemon_api.get_new_token()

    # uncomment this and comment all lines from scrape_data() function to find_gm_tickers() function in main() to use saved data
    # headlines = pd.read_csv("tickers_scores.csv")

    headlines = get_isins(headlines)

    print(f"The highest sentiment score is: {headlines['score'].max()}")
    print(f"The lowest sentiment score is {headlines['score'].min()}")

    orders = place_trades(headlines)
    activate_order(orders)


if __name__ == "__main__":
    main()
