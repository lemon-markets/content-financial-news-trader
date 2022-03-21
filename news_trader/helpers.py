#from datetime import datetime, timedelta
import datetime
import os
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
                except Exception as e:
                    print(e)
                    raise
                else:
                    if instrument.get("total") > 0:
                        isins.append(instrument.get("results")[0].get("isin"))
                    else:
                        isins.append("NA")
        headlines.set_isins(isins)

    def place_trades(self, buy: List[str], sell: List[str]):
        orders = []

        expires_at = "p0d"

        # place buy orders
        for isin in buy:
            side = "buy"
            quantity = 1
            order = self._lemon_api.place_order(
                isin, expires_at, quantity, side
            )
            orders.append(order)
            print(f"You are {side}ing {quantity} share(s) of instrument {isin}.")

        positions = self._lemon_api.get_positions()
        positions_isins = []

        for item in positions:
            positions_isins.append(item.get("isin"))

        # place sell orders
        for isin in sell:
            if isin in positions_isins:
                side = "sell"
                quantity = 1
                order = self._lemon_api.place_order(
                    isin, expires_at, quantity, side
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
            self._lemon_api.activate_order(order["results"].get("id"))
            print(f'Activated {order["results"].get("isin")}')
        return orders

    def is_venue_open(self):
        return self._lemon_api.get_venue()["is_open"]

    def seconds_until_open(self):
        venue = self._lemon_api.get_venue()
        today = datetime.datetime.today()
        next_opening_time = datetime.datetime.strptime(venue["opening_hours"]["start"], "%H:%M")
        next_opening_day = datetime.datetime.strptime(venue["opening_days"][0], "%Y-%m-%d")

        date_difference = next_opening_day - today
        days = date_difference.days + 1
        if not self.is_venue_open():
            print("Trading venue is not open")
            time_delta = datetime.datetime.combine(
                datetime.datetime.now().date() + datetime.timedelta(days=1), next_opening_time.time()
            ) - datetime.datetime.now()
            print(time_delta.seconds + (days * 86400))
            return time_delta.seconds
        else:
            print("Trading venue is open")
            return 0
