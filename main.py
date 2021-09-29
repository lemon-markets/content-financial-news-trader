import os

import requests
import pandas as pd
import datetime
import pprint
import time

from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from models.FIGI import FIGI
from models.Instrument import Instrument
from models.Space import Space
from models.Token import Token
from models.Order import Order


def scrape_data(base_url: str, url_endpoints: list):
    """Scrapes headline, ticker and date from articles as presented on MarketWatch"""
    headlines = []

    for url in url_endpoints:
        page = requests.get(base_url + url)
        soup = BeautifulSoup(page.content, 'html.parser')
        article_contents = soup.find_all('div', class_='article__content')

        for article in article_contents:
            # determine whether ticker present
            ticker = article.find('span', class_='ticker__symbol')

            # if ticker present in article, add both ticker and headline to list
            if ticker is not None:
                headline = article.find('a', class_='link').text.strip()
                timestamp = article.find('span', class_='article__timestamp')
                if timestamp is not None:
                    time_stamp = timestamp['data-est']
                # if no timestamp, assume current article and initialise timestamp to now
                else:
                    time_stamp = datetime.datetime.now()

                head_and_tick = [headline, ticker.text, time_stamp]
                headlines.append(head_and_tick)

    columns = ['headline', 'ticker', 'timestamp']
    headlines_df = pd.DataFrame(headlines, columns=columns)
    return headlines_df


def filter_dataframe(dataframe, removable_tickers: list):
    return dataframe[~dataframe.loc[:, 'ticker'].isin(removable_tickers)].copy()


def sentiment_analysis(dataframe):
    # initialise VADER
    vader = SentimentIntensityAnalyzer()
    scores = []

    # perform sentiment analysis
    for headline in dataframe.loc[:, 'headline']:
        score = vader.polarity_scores(headline).get('compound')
        scores.append(score)

    # append scores to DataFrame
    dataframe.loc[:, 'score'] = scores

    return dataframe


def aggregate_scores(dataframe):
    # dataframe = sentiment_analysis(dataframe)
    grouped_tickers = dataframe.groupby('ticker').mean()
    grouped_tickers.reset_index(level=0, inplace=True)

    return grouped_tickers



def find_gm_tickers(dataframe):
    gm_tickers = []
    iteration = 1

    for ticker in dataframe.loc[:, 'ticker']:
        print(ticker)
        job = {'query': ticker, 'exchCode': 'GM'}
        gm_ticker = FIGI().search_jobs(job)
        print(gm_ticker)
        if gm_ticker.get('data'):
            gm_tickers.append(gm_ticker.get('data')[0].get('ticker'))
        else:
            gm_tickers.append('Ticker not found')
        iteration += 1
        if iteration % 20 == 0:
            time.sleep(60)
    dataframe.loc[:, 'gm_ticker'] = gm_tickers

    return dataframe


def get_isins(dataframe):
    isins = []

    for ticker in dataframe.loc[:, 'gm_ticker']:
        if ticker == 'Ticker not found':
            isins.append('No ISIN found.')
        else:
            instrument = Instrument().get_instrument(ticker)

            if instrument.get('count') != 0:
                isins.append(instrument.get('results')[0].get('isin'))
            else:
                isins.append('No ISIN found.')

    dataframe.loc[:, 'isin'] = isins
    return dataframe


def trade_decision(dataframe):
    buy = []
    sell = []
    for index, row in dataframe.iterrows():
        if row['score'] > 0.5 and row['isin'] != 'No ISIN found':
            print(f'Buy {row["ticker"]} with sentiment score {row["score"]} and ISIN {row["isin"]}')
            buy.append(row['isin'])
        if row['score'] < -0.5 and row['isin'] != 'No ISIN found':
            print(f'Sell {row["ticker"]} with sentiment score {row["score"]} and ISIN {row["isin"]}')
            sell.append(row['isin'])

    return buy, sell


def place_trades(dataframe):
    buy, sell = trade_decision(dataframe)

    orders = []

    space_uuid = Space().get_space_uuid()
    valid_time = (datetime.datetime.now() + datetime.timedelta(hours=1)).timestamp()

    # place buy orders
    for isin in buy:
        side = 'buy'
        order = Order().place_order(isin, valid_time, 1, side, space_uuid)
        orders.append(order)
        print(order)

    # place sell orders
    for isin in sell:
        side = 'sell'
        order = Order().place_order(isin, valid_time, 1, side, space_uuid)
        orders.append(order)
        print(order)

    return orders


def activate_order(orders):
    for order in orders:
        Order().activate_order(order.get('uuid'), Space().get_space_uuid())
        print(f'Activated {order.get("isin")}')
    return orders


def main():
    # import data source
    pd.options.display.max_columns = None
    pd.options.display.max_rows = None

    base_url = 'https://www.marketwatch.com/investing/'
    url_endpoints = ['barrons', 'aerospace-defense', 'autos', 'biotech', 'energy', 'health-care', 'media',
                     'pharmaceutical',
                     'retail', 'telecommunications', 'airlines', 'banking', 'food-beverage', 'internet-online-services',
                     'metals-mining', 'real-estate-construction', 'software', 'technology']

    headlines = scrape_data(base_url, url_endpoints)
    print(headlines.head())

    removable_tickers = ['SPX', 'DJIA', 'BTCUSD', '', 'GCZ21', 'HK:3333', 'DX:DAX', 'XE:VOW', 'UK:AZN', 'GBPUSD',
                         'CA:WEED', 'UK:UKX', 'CA:ACB', 'CA:ACB', 'CA:CL', 'BX:TMUBMUSD10Y',]
    headlines = filter_dataframe(headlines, removable_tickers)
    print(headlines)

    headlines = sentiment_analysis(headlines)
    print(headlines)

    headlines = aggregate_scores(headlines)
    print(headlines)

    headlines = find_gm_tickers(headlines)
    print(headlines)

    headlines = get_isins(headlines)
    print(headlines)

    print(f"The highest sentiment score is: {headlines['score'].max()}")
    print(f"The lowest sentiment score is {headlines['score'].min()}")

    orders = place_trades(headlines)
    print(orders)
    activate_order(orders)


if __name__ == '__main__':
    main()
