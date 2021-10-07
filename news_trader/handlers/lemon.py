import os
from functools import cached_property
from typing import List

import requests


class RequestHandler:
    def __init__(self, token):
        self.token = token or os.environ.get("TOKEN_KEY")
        self.auth_url: str = os.environ.get("AUTH_URL")
        self.url_trading: str = os.environ.get("TRADING_URL")
        self.url_market: str = os.environ.get("MARKET_URL")

    def get_token(self, endpoint: str, data: dict):
        response = requests.post(self.auth_url + endpoint, data)
        return response

    def get_data_trading(self, endpoint: str):
        response = requests.get(self.url_trading + endpoint, headers=self.headers)
        return response.json()

    def get_data_market(self, endpoint: str):
        response = requests.get(self.url_market + endpoint, headers=self.headers)
        return response.json()

    def put_data(self, endpoint: str):
        response = requests.put(self.url_trading + endpoint, headers=self.headers)
        return response.json()

    def post_data(self, endpoint: str, data):
        response = requests.post(
            self.url_trading + endpoint, data, headers=self.headers
        )
        return response.json()

    @property
    def headers(self):
        return {"Authorization": f"Bearer {self.token}"}


class LemonMarketsAPI:
    def get_instrument(self, query: str):
        return self.handler.get_data_market(f"instruments/?search={query}&type=stock")

    def place_order(
        self, isin: str, valid_until: float, quantity: int, side: str, space_uuid: str
    ):
        order_details = {
            "isin": isin,
            "valid_until": valid_until,
            "side": side,
            "quantity": quantity,
        }
        return self.handler.post_data(f"spaces/{space_uuid}/orders/", order_details)

    def activate_order(self, order_uuid: str, space_uuid: str):
        return self.handler.put_data(
            f"spaces/{space_uuid}/orders/{order_uuid}/activate/"
        )

    def get_portfolio(self, space_uuid) -> list:
        return self.handler.get_data_trading(f"spaces/{space_uuid}/portfolio/")[
            "results"
        ]

    def get_space_uuid(self):
        return self.handler.get_data_trading("spaces")["results"][0]["uuid"]

    @cached_property
    def handler(self):
        token_details = {
            "client_id": os.getenv("CLIENT_ID"),
            "client_secret": os.getenv("CLIENT_SECRET"),
            "grant_type": "client_credentials",
        }

        response = self.handler.get_token("oauth2/token", token_details)
        token = response.json().get("access_token", None)

        return RequestHandler(token)

    def get_isins_by_gm_tickers(self, gm_tickers: List[str]) -> List[str]:
        isins = []

        for ticker in gm_tickers:
            if ticker == "NA":
                isins.append("NA")
                continue

            try:
                instrument = self.get_instrument(ticker)
            except Exception as e:
                print(e)
            else:
                isin = "NA"
                if instrument["count"] > 0:
                    isin = instrument["results"][0]["isin"]

                isins.append(isin)

        return isins
