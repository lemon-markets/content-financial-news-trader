from functools import cached_property
from typing import List

import pandas as pd

from nltk.sentiment.vader import SentimentIntensityAnalyzer

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


class HeadLines:
    def __init__(self, dataframe: pd.DataFrame):
        self._df = dataframe

        # pre-emptively decide on some tickers to exclude to make dataset smaller
        self._df = self._df[~self._df.loc[:, "ticker"].isin(REMOVABLE_TICKERS)].copy()
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

    def get_trade_decisions(self):
        buy = []
        sell = []
        for index, row in self._df.iterrows():
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

    @property
    def raw_dataframe(self) -> pd.DataFrame:
        return self._df
