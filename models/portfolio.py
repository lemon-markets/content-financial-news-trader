from helpers import RequestHandler


class Portfolio(RequestHandler):
    def get_portfolio(self, space_uuid) -> list:
        endpoint = f"spaces/{space_uuid}/portfolio/"
        response = self.get_data_trading(endpoint)
        return response["results"]
