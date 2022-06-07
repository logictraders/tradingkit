import json
import logging
from datetime import datetime
import csv
from dateutil.relativedelta import relativedelta
from dateutil import parser

from tradingkit.utils.system import System
from tradingkit.data.feed.backtest_feeder import BacktestFeeder
from tradingkit.pubsub.core.publisher import Publisher
from tradingkit.pubsub.event.trade import Trade
from tradingkit.pubsub.event.funding import Funding
import time


class FundingBacktestFeeder(BacktestFeeder, Publisher):
    def __init__(self, exchange='kraken', symbol='BTC/EUR', since8601=None, to8601=None):
        super().__init__(exchange, symbol, since8601, to8601)
        self.founding_rate_data = None
        self.next_founding_rate_index = 0
        self.name = 'bitmex'

    def dispatch_month(self, exchange, symbol, year, month, since, to):
        import_dir = System.get_import_dir()
        base, quote = symbol.split('/')
        full_filename = '%s/%s-%s_%s-%d-%02d.json' % (import_dir, exchange, base, quote, year, month)

        for trade in json.load(open(full_filename, 'r')):
            if since.timestamp() <= trade['timestamp'] / 1000 < to.timestamp():
                self.dispatch_founding_rate(trade, exchange, base, quote)
                trade['exchange'] = self.name
                #time.sleep(100000)
                self.dispatch(Trade(trade))

    def dispatch_founding_rate(self, trade, exchange, base, quote):
        """Updates the founding rate"""
        if self.founding_rate_data is None:
            import_dir = System.get_import_dir()
            full_filename = '%s/funding_bitmex-%s_%s.json' % (import_dir, base, quote)

            self.founding_rate_data = []
            first_rate_timestamp = trade['timestamp'] - 8 * 60 * 60 * 1000
            for row in json.load(open(full_filename, 'r')):
                rate = float(row['fundingRate'])
                timestamp = int(parser.isoparse(row['timestamp']).timestamp() * 1000)
                if timestamp > first_rate_timestamp:
                    self.founding_rate_data.append({"timestamp": timestamp,
                                                    "rate": rate,
                                                    "date": row['timestamp'],
                                                    "price": trade['price'],
                                                    "symbol": trade['symbol']})
            self.founding_rate_data[0]['exchange'] = self.name
            #time.sleep(100000)
            self.dispatch(Funding(self.founding_rate_data[0]))
            self.next_founding_rate_index += 1

        elif self.next_founding_rate_index < len(self.founding_rate_data) and \
                trade['timestamp'] > self.founding_rate_data[self.next_founding_rate_index]["timestamp"]:
            self.founding_rate_data[self.next_founding_rate_index]['exchange'] = self.name
            self.dispatch(Funding(self.founding_rate_data[self.next_founding_rate_index]))
            self.next_founding_rate_index += 1





