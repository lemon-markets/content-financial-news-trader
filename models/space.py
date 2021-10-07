from helpers import RequestHandler


class Space(RequestHandler):
    def get_space_uuid(self):
        endpoint = f"spaces"
        response = self.get_data_trading(endpoint)["results"]
        return response[0]["uuid"]
