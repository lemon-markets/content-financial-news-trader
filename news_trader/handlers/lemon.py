import os

import requests


class RequestHandler:
    def __init__(self):
        self.token = os.getenv("TOKEN_KEY")
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
    def __init__(self):
        self._handler = RequestHandler()

    def get_instrument(self, query: str):
        endpoint = f"instruments/?search={query}&type=stock"
        return self._handler.get_data_market(endpoint)

    def place_order(
        self, isin: str, valid_until: float, quantity: int, side: str, space_uuid: str
    ):
        order_details = {
            "isin": isin,
            "valid_until": valid_until,
            "side": side,
            "quantity": quantity,
        }
        endpoint = f"spaces/{space_uuid}/orders/"
        response = self._handler.post_data(endpoint, order_details)
        return response

    def activate_order(self, order_uuid: str, space_uuid: str):
        endpoint = f"spaces/{space_uuid}/orders/{order_uuid}/activate/"
        response = self._handler.put_data(endpoint)
        return response

    def get_portfolio(self, space_uuid) -> list:
        endpoint = f"spaces/{space_uuid}/portfolio/"
        response = self._handler.get_data_trading(endpoint)
        return response["results"]

    def get_space_uuid(self):
        endpoint = f"spaces"
        response = self._handler.get_data_trading(endpoint)["results"]
        return response[0]["uuid"]

    def get_new_token(self):
        token_details = {
            "client_id": os.getenv("CLIENT_ID"),
            "client_secret": os.getenv("CLIENT_SECRET"),
            "grant_type": "client_credentials",
        }

        endpoint = "oauth2/token"
        response = self._handler.get_token(endpoint, token_details)
        self._handler.token = response.json().get("access_token", None)

        return self._handler.token
