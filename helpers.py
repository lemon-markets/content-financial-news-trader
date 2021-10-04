import os
import requests
from dotenv import load_dotenv


class RequestHandler():

    def __init__(self):
        load_dotenv()
        self.headers = {'Authorization': f'Bearer ' + os.getenv('TOKEN_KEY')}
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
        response = requests.post(self.url_trading + endpoint,
                                 data,
                                 headers=self.headers)
        return response.json()
