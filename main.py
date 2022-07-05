import os

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from pytz import utc
from lemon import api

from news_trader.handlers.figi import FigiAPI
from news_trader.handlers.marketwatch import MarketWatchAPI
from news_trader.headlines import HeadLines
from news_trader.helpers import Helpers

load_dotenv()
helpers: Helpers = Helpers()

client = api.create(
    trading_api_token=os.getenv("TRADING_API_KEY"),
    market_data_api_token=os.getenv("DATA_API_KEY"),
    env="paper"
)


def sentiment_analysis():
    figi_api: FigiAPI = FigiAPI()
    market_watch_api: MarketWatchAPI = MarketWatchAPI()
    venue = helpers.client.market_data.venues.get(os.getenv('MIC')).results[0]
    if not venue.is_open:
        print(f"Venue is not open. Next opening day is {venue.opening_days[0].day}-{venue.opening_days[0].month}"
              f"-{venue.opening_days[0].year}")
        return
    # COMMENT FROM HERE...
    headlines: HeadLines = market_watch_api.get_headlines()

    headlines.sentiment_analysis()
    headlines.aggregate_scores()

    gm_tickers = figi_api.find_gm_tickers(headlines.get_tickers())
    headlines.set_gm_tickers(gm_tickers)

    headlines.raw_dataframe.to_csv("tickers_scores.csv")
    # ...UP TO THIS POINT TO USE SAVED DATA

    # uncomment lines below and comment all tagged lines above to use saved data
    # import pandas as pd
    # headlines = HeadLines(pd.read_csv("tickers_scores.csv"))
    helpers.get_isins(headlines)

    print(f"The highest sentiment score is: {headlines.max_score}")
    print(f"The lowest sentiment score is {headlines.min_score}")

    buy, sell = headlines.get_trade_decisions()
    order_ids = helpers.place_trades(buy, sell)
    helpers.activate_order(order_ids=order_ids)


if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone=utc)

    sentiment_analysis()
    # reschedule your trades for the future years ad infinitum
    scheduler.add_job(sentiment_analysis,
                      trigger=CronTrigger(day_of_week="mon-fri",
                                          hour=10,
                                          minute=30,
                                          timezone=utc))

    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
