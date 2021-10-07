import os
import requests


class FIGI:
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
