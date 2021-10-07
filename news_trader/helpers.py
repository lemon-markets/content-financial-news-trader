from datetime import datetime, timedelta
from typing import List

from news_trader.handlers.lemon import LemonMarketsAPI
from news_trader.headlines import HeadLines


class Helpers:
    def __init__(self, lemon_api: LemonMarketsAPI):
        self._lemon_api = lemon_api

    def get_isins(self, headlines: HeadLines):
        isins = []

        for ticker in headlines.get_gm_tickers():
            if ticker == "NA":
                isins.append("NA")

            else:
                try:
                    instrument = self._lemon_api.get_instrument(ticker)

                    if instrument.get("count") > 0:
                        isins.append(instrument.get("results")[0].get("isin"))
                    else:
                        isins.append("NA")

                except Exception as e:
                    print(e)

        headlines.set_isins(isins)

    def place_trades(self, buy: List[str], sell: List[str]):
        orders = []

        space_uuid = self._lemon_api.get_space_uuid()
        valid_time = (datetime.now() + timedelta(hours=1)).timestamp()

        # place buy orders
        for isin in buy:
            side = "buy"
            quantity = 1
            order = self._lemon_api.place_order(
                isin, valid_time, quantity, side, space_uuid
            )
            orders.append(order)
            print(f"You are {side}ing {quantity} share(s) of instrument {isin}.")

        portfolio = self._lemon_api.get_portfolio(space_uuid)

        # place sell orders
        for isin in sell:
            if isin in portfolio:
                side = "sell"
                quantity = 1
                order = self._lemon_api.place_order(
                    isin, valid_time, quantity, side, space_uuid
                )
                orders.append(order)
                print(f"You are {side}ing {quantity} share(s) of instrument {isin}.")
            else:
                print(
                    f"You do not have sufficient holdings of instrument {isin} to place a sell order."
                )

        return orders

    def activate_order(self, orders):
        for order in orders:
            space_id = self._lemon_api.get_space_uuid()
            self._lemon_api.activate_order(order.get("uuid"), space_id)
            print(f'Activated {order.get("isin")}')
        return orders
