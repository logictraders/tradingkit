import sys
import time

from ccxt import DDoSProtection, RequestTimeout, Exchange, ExchangeError

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
            except ExchangeError as ex:
                if 'Too many requests' in str(ex):
                    sys.stderr.write("Api call rate limit reached, waiting %d seconds...\n" % self.wait_seconds)
                    time.sleep(self.wait_seconds)
                else:
                    template = "An  exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print(message)
                    sys.exit(-1)


    def fetch_all(self, symbol, since8601, to8601=None, candles=False):
        trades = []
        last_trade = None
        lo_trade = None
        hi_trade = None
        pst = 0.01
        for step in self.fetch(symbol, since8601, to8601):
            for trade in step:

                if last_trade is None:
                    last_trade = trade.copy()
                    lo_trade = trade.copy()
                    hi_trade = trade.copy()

                elif trade['price'] < lo_trade['price']:
                    lo_trade = trade.copy()

                elif trade['price'] > hi_trade['price']:
                    hi_trade = trade.copy()

                if hi_trade['price'] / lo_trade['price'] - 1 > pst:

                    if lo_trade['timestamp'] < hi_trade ['timestamp']:
                        # print("LO", datetime.fromtimestamp(trade['timestamp'] / 1000), lo_trade['price'],
                        #       hi_trade['price'])
                        # print(lo_trade['price'], )
                        # print(hi_trade['price'])
                        trades.append(lo_trade)
                        trades.append(hi_trade)
                        if candles:
                            self.trade_to_candle(lo_trade)
                            self.trade_to_candle(hi_trade)
                    else:
                        # print("HI", datetime.fromtimestamp(trade['timestamp'] / 1000), hi_trade['price'],
                        #       lo_trade['price'])
                        # print(hi_trade['price'])
                        # print(lo_trade['price'])
                        trades.append(hi_trade)
                        trades.append(lo_trade)
                        if candles:
                            self.trade_to_candle(hi_trade)
                            self.trade_to_candle(lo_trade)
                    last_trade = trade.copy()
                    lo_trade = trade.copy()
                    hi_trade = trade.copy()

                #print(round(lo_trade['price'], 2), trade['price'], round(hi_trade['price'], 2), hi_trade['price'] / lo_trade['price'])

            if lo_trade['timestamp'] < hi_trade['timestamp']:
                # print("LO___", datetime.fromtimestamp(trade['timestamp'] / 1000), lo_trade['price'],
                #       hi_trade['price'])
                # print(lo_trade['price'])
                # print(hi_trade['price'])
                trades.append(lo_trade)
                trades.append(hi_trade)
                if candles:
                    self.trade_to_candle(lo_trade)
                    self.trade_to_candle(hi_trade)
            else:
                # print("HI___", datetime.fromtimestamp(trade['timestamp'] / 1000), hi_trade['price'],
                #       lo_trade['price'])
                # print(hi_trade['price'])
                # print(lo_trade['price'])
                trades.append(hi_trade)
                trades.append(lo_trade)
                if candles:
                    self.trade_to_candle(hi_trade)
                    self.trade_to_candle(lo_trade)
            last_trade = trade.copy()
            lo_trade = trade.copy()
            hi_trade = trade.copy()
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