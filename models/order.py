from helpers import RequestHandler


class Order(RequestHandler):
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
        response = self.post_data(endpoint, order_details)
        return response

    def activate_order(self, order_uuid: str, space_uuid: str):
        endpoint = f"spaces/{space_uuid}/orders/{order_uuid}/activate/"
        response = self.put_data(endpoint)
        return response
