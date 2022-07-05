import os
from typing import List

from lemon import api

from news_trader.headlines import HeadLines


class Helpers:
    def __init__(self):
        self.client = api.create(
            trading_api_token=os.getenv("TRADING_API_KEY"),
            market_data_api_token=os.getenv("DATA_API_KEY"),
            env="paper"
        )

    def get_isins(self, headlines: HeadLines):
        isins = []

        for ticker in headlines.get_gm_tickers():
            if ticker == "NA":
                isins.append("NA")
            else:
                try:
                    instruments = self.client.market_data.instruments.get(search=ticker, type="stock")
                except Exception as e:
                    print(e)
                    raise
                else:
                    if instruments.total > 0:
                        isins.append(instruments.results[0].isin)
                    else:
                        isins.append("NA")
        headlines.set_isins(isins)

    def place_trades(self, buy: List[str], sell: List[str]):
        order_ids = []

        expires_at = 0
        quantity = 1

        # place buy orders
        for isin in buy:
            side = "buy"
            if isin == "NA":
                continue
            price = self.client.market_data.quotes.get_latest(isin=isin).results[0].a * quantity
            if price < 50:
                print(f"Order cannot be placed as total price, €{price}, is less than minimum order amount of €50.")
                continue
            order = self.client.trading.orders.create(
                isin=isin, expires_at=expires_at, quantity=quantity, side=side
            )
            order_ids.append(order.results.id)
            print(f"You are {side}ing {quantity} share(s) of instrument {isin}.")

        positions = self.client.trading.positions.get().results
        positions_isins = []

        for item in positions:
            positions_isins.append(item.isin)

        # place sell orders
        for isin in sell:
            if isin == "NA":
                continue
            if isin in positions_isins:
                side = "sell"
                price = self.client.market_data.quotes.get_latest(isin=isin).results[0].b * quantity
                if price < 50:
                    print(f"Order cannot be placed as total price, €{price}, is less than minimum order amount of €50.")
                    continue
                order = self.client.trading.orders.create(
                    isin=isin, expires_at=expires_at, quantity=quantity, side=side
                )
                order_ids.append(order.results.id)
                print(f"You are {side}ing {quantity} share(s) of instrument {isin}.")
            else:
                print(
                    f"You do not have sufficient holdings of instrument {isin} to place a sell order."
                )

        return order_ids

    def activate_order(self, order_ids):
        for order_id in order_ids:
            self.client.trading.orders.activate(order_id)
            print(f'Activated {self.client.trading.orders.get_order(order_id=order_id).results.isin_title}')
        return order_ids
