import os
import requests


class FIGI:
    # def __init__(self):
    #     self.figi_url: str = os.getenv("OPENFIGI_URL")
    #     self.figi_key: str = os.getenv("OPENFIGI_KEY")
    #     #self.headers: dict = {'Content-Type': 'text/json', 'X-OPENFIGI-APIKEY': self.figi_key}

    def search_jobs(self, jobs: dict):
        headers = {
            "Content-Type": "text/json",
            "X-OPENFIGI-APIKEY": os.environ.get("OPENFIGI_KEY"),
        }
        response = requests.post(
            url=os.environ.get("OPENFIGI_URL"), headers=headers, json=jobs
        )

        if response.status_code != 200:
            raise Exception(f"Bad response code {response.status_code}")

        return response.json()
