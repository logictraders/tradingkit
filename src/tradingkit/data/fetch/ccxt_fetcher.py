import sys
import time

from ccxt import DDoSProtection, RequestTimeout, Exchange

from tradingkit.data.fetch.fetcher import Fetcher


class CCXTFetcher(Fetcher):
    def __init__(self, exchange: Exchange):
        self.exchange = exchange
        self.wait_seconds = 60

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
                    last_trade = trade.copy()
            trades.append(last_trade)
            print("ACC trades", len(trades))
        return trades