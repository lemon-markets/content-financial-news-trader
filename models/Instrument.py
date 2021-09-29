import os
import random

from helpers import RequestHandler


class Instrument(RequestHandler):

    def get_instrument(self, query: str):
        endpoint = f'instruments/?search={query}'
        response = self.get_data_market(endpoint)
        return response.json().get('results')[0].get('isin')