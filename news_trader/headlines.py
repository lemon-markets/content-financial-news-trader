from functools import cached_property
from typing import List

import pandas as pd

from nltk.sentiment.vader import SentimentIntensityAnalyzer

from news_trader.handlers.figi import FIGI
from news_trader.handlers.lemon import LemonMarketsAPI


class HeadLines:
    def __init__(self, dataframe: pd.DataFrame):
        self._df = dataframe
        self._figi_api = FIGI()
        self._lemon_api = LemonMarketsAPI()

    def remove_tickers(self, removable_tickers: list):
        self._df = self._df[~self._df.loc[:, "ticker"].isin(removable_tickers)].copy()
        print(self._df.head())

    def sentiment_analysis(self):
        scores = []

        # perform sentiment analysis
        for headline in self._df.loc[:, "headline"]:
            score = self.vader.polarity_scores(headline).get("compound")
            scores.append(score)

        # append scores to DataFrame
        self._df.loc[:, "score"] = scores
        print(self._df.head())

    def aggregate_scores(self):
        self._df = self._df.groupby("ticker").mean()
        self._df.reset_index(level=0, inplace=True)
        print(self._df.head())

    def get_tickers(self):
        return self._df.loc[:, "ticker"]

    def set_gm_tickers(self, gm_tickers: list):
        self._df.loc[:, "gm_ticker"] = gm_tickers
        print(self._df.head())

    def get_gm_tickers(self):
        return self._df.loc[:, "gm_ticker"]

    def set_isins(self, isins: List[str]):
        self._df.loc[:, "isin"] = isins
        print(self._df)

    def save(self, filename="tickers_scores.csv"):
        self._df.to_csv(filename)

    @property
    def max_score(self):
        return self._df["score"].max()

    @property
    def min_score(self):
        return self._df["score"].min()

    @cached_property
    def vader(self):
        # initialise VADER
        try:
            return SentimentIntensityAnalyzer()
        except LookupError:
            import nltk

            nltk.download("vader_lexicon")
            return SentimentIntensityAnalyzer()
