import sys
import time

from ccxt import DDoSProtection, RequestTimeout, Exchange

from tradingkit.data.fetch.fetcher import Fetcher
from datetime import datetime


class CCXTFetcher(Fetcher):
    def __init__(self, exchange: Exchange):
        self.exchange = exchange
        self.wait_seconds = 60

        self.candles = None
        self.last_candle = None
        self.timeframes = {"1m": 60,
                           "5m": 300,
                           "15m": 900,
                           "30m": 1800,
                           "1H": 3600,
                           "4H": 14400,
                           "6H": 21600,
                           "12H": 43200,
                           "1D": 86400,
                           "2D": 172800,
                           "4D": 345600,
                           "1W": 604800,
                           "2W": 1209600,
                           "1_M": 2629800}

    def fetch(self, symbol, since8601=None, to8601=None):
        since = 0 if since8601 is None else self.exchange.parse8601(since8601)
        to = self.exchange.milliseconds() if to8601 is None else self.exchange.parse8601(to8601)
        end = False
        while since < to and not end:
            try:
                sys.stdout.write("Since %s\n" % (time.ctime(since // 1000)))
                step = self.exchange.fetch_trades(symbol, since)
                if len(step) > 0:
                    if since != step[-1]['timestamp']:
                        since = step[-1]['timestamp']
                        yield step
                    else:
                        sys.stdout.write("More trades in one millisecond than response length\n")
                        since += 1
                else:
                    sys.stdout.write("End of trades\n")
                    end = True
            except DDoSProtection:
                sys.stderr.write("Api call rate limit reached, waiting %d seconds...\n" % self.wait_seconds)
                time.sleep(self.wait_seconds)
            except RequestTimeout:
                sys.stderr.write("Request timeout, retrying...\n")

    def fetch_all(self, symbol, since8601, to8601=None):
        trades = []
        last_trade = None
        for step in self.fetch(symbol, since8601, to8601):
            for trade in step:
                if last_trade is None:
                    last_trade = trade.copy()
                elif last_trade['price'] == trade['price'] and last_trade['side'] == trade['side']:
                    last_trade['amount'] += trade['amount']
                    # last_trade['cost'] += trade['cost']  # on some exchanges is None
                else:
                    trades.append(last_trade)
                    self.trade_to_candle(last_trade)
                    last_trade = trade.copy()
            trades.append(last_trade)
            print("ACC trades", len(trades))
        return [trades, self.candles]

    def trade_to_candle(self, trade):

        if self.candles is None:
            self.candles = {x:{} for x in self.timeframes.keys()}

        if self.last_candle is None:
            self.last_candle = {x:None for x in self.timeframes.keys()}

        for tf in self.timeframes.keys():
            sec = self.timeframes[tf]
            key = trade['timestamp'] // (sec * 1000) * sec
            key = str(datetime.fromtimestamp(key))
            if self.last_candle[tf] is not None and key in self.candles[tf]:
                self.candles[tf][key]['high'] = max(self.candles[tf][key]['high'], trade['price'])
                self.candles[tf][key]['low'] = min(self.candles[tf][key]['low'], trade['price'])
                self.candles[tf][key]['close'] = trade['price']
                self.candles[tf][key]['vol'] += trade['amount']
                self.candles[tf][key]['cost'] += trade['cost']
                self.candles[tf][key]['trades'] += 1
            else:
                self.candles[tf][key] = {
                    'datetime': key,
                    'open': trade['price'],
                    'high': trade['price'],
                    'low': trade['price'],
                    'close': trade['price'],
                    'vol': trade['amount'],
                    'cost': trade['cost'],
                    'trades': 1,
                    'timeframe': tf
                }
            self.last_candle[tf] = self.candles[tf][key]