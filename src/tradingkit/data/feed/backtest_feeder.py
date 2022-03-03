import json
import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta

from tradingkit.utils.system import System
from tradingkit.data.feed.feeder import Feeder
from tradingkit.pubsub.core.publisher import Publisher
from tradingkit.pubsub.event.trade import Trade
from ccxt import InsufficientFunds


class BacktestFeeder(Feeder, Publisher):
    def __init__(self, exchange='kraken', symbol='BTC/EUR', since8601=None, to8601=None):
        super().__init__()
        self.since = datetime.fromisoformat(since8601)
        self.to = datetime.fromisoformat(to8601)
        self.symbol = symbol
        self.exchange = exchange

    def feed(self):
        start_month = self.since.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_month = self.to.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        while start_month <= end_month:
            try:
                self.dispatch_month(
                    self.exchange,
                    self.symbol,
                    start_month.year,
                    start_month.month,
                    self.since,
                    self.to
                )
                start_month += relativedelta(months=1)
            except FileNotFoundError as e:
                if start_month.timestamp() < datetime.now().timestamp():
                    logging.warning("Import file not found, use command 'tk import' before")
                    raise e
                break

            except InsufficientFunds as e:
                print("InsufficientFunds: Executed Liquidation")
                break

    def dispatch_month(self, exchange, symbol, year, month, since, to):
        import_dir = System.get_import_dir()
        base, quote = symbol.split('/')
        full_filename = '%s/%s-%s_%s-%d-%02d.json' % (import_dir, exchange, base, quote, year, month)

        for trade in json.load(open(full_filename, 'r')):
            if since.timestamp() <= trade['timestamp'] / 1000 < to.timestamp():
                trade['exchange'] = self.exchange
                self.dispatch(Trade(trade))
