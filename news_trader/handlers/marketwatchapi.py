from datetime import datetime

import requests
import pandas as pd
from dateutil.parser import isoparse
from bs4 import BeautifulSoup

from news_trader.headlines import HeadLines

BASE_URL = "https://www.marketwatch.com/investing/"

URL_ENDPOINTS = [
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


class MarketWatchAPI:
    def get_headlines(self) -> HeadLines:
        """Scrapes headline, ticker and date from articles as presented on MarketWatch"""
        headlines = []

        for url in URL_ENDPOINTS:
            page = requests.get(BASE_URL + url)
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
                        time_stamp = datetime.now()

                    head_and_tick = [headline, ticker.text, time_stamp]
                    headlines.append(head_and_tick)

        columns = ["headline", "ticker", "timestamp"]
        headlines_df = pd.DataFrame(headlines, columns=columns)
        print(headlines_df.head())

        return HeadLines(headlines_df)
