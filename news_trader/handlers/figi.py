import os
import time
from typing import List

import requests


class FigiAPI:
    def __init__(self):
        self._api_key = os.environ.get("OPENFIGI_KEY")
        self._url = os.environ.get("OPENFIGI_URL")

    def search_jobs(self, jobs: dict):
        headers = {
            "Content-Type": "text/json",
            "X-OPENFIGI-APIKEY": self._api_key,
        }
        response = requests.post(url=self._url, headers=headers, json=jobs)

        if response.status_code != 200:
            raise Exception(f"Bad response code {response.status_code}")

        return response.json()

    def find_gm_tickers(self, tickers: List[str]) -> List[str]:
        print("Collecting tickers...")

        gm_tickers = []
        iteration = 1

        for ticker in tickers:
            job = {"query": ticker, "exchCode": "GM"}
            gm_ticker = self.search_jobs(job)

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
        return gm_tickers
