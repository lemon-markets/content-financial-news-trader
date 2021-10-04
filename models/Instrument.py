from helpers import RequestHandler


class Instrument(RequestHandler):

    def get_instrument(self, query: str):
        endpoint = f'instruments/?search={query}&type=stock'
        response = self.get_data_market(endpoint)
        return response
