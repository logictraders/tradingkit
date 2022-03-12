import logging
from abc import ABC, abstractmethod

from ccxt import Exchange

from tradingkit.pubsub.core.event import Event
from tradingkit.pubsub.core.publisher import Publisher
from tradingkit.pubsub.core.subscriber import Subscriber


class Strategy(Publisher, Subscriber, ABC):

    def __init__(self, exchange: Exchange, config=None):
        super().__init__()
        self.exchange = exchange
        self.config = config
        self.start_equity = None
        self.is_started = False
        self.start_base_balance = None
        self.start_base_equity = None

    @abstractmethod
    def get_symbol(self):
        pass

    def start(self):
        logging.info("Start strategy %s" % str(self.__class__))
        balance = self.exchange.fetch_balance()['total']
        symbol = self.config['symbol']
        base, quote = symbol.split('/')
        quote_balance = balance[quote] if quote in balance else 0
        self.start_equity = quote_balance + balance[base] * self.exchange.fetch_ticker(symbol)['bid']
        self.start_base_equity = quote_balance / self.exchange.fetch_ticker(symbol)['bid'] + balance[base]
        self.start_base_balance = balance[base]
        logging.info("Initial Equity: %s" % str(self.start_equity))

    def on_event(self, event: Event):
        if not self.is_started:
            self.is_started = True
            self.start()

    def finish(self):
        logging.info("Finish strategy %s" % str(self.__class__))
        balance = self.exchange.fetch_balance()['total']
        symbol = self.config['symbol']
        base, quote = symbol.split('/')
        price = self.exchange.fetch_ticker(symbol)['bid']
        end_equity = balance[quote] + balance[base] * price
        end_base_equity = balance[quote] / price + balance[base]
        try:
            position = self.exchange.private_get_position()[0]
            pnl = (price / position['avgEntryPrice'] - 1) * position['currentQty']
        except Exception as e:
            pnl = 0
        end_equity += pnl
        logging.info("Final Balances: %s" % str(balance))
        logging.info("Equity: %.2f EUR" % end_equity)

        return {
            "start_equity": self.start_equity,
            "end_equity": end_equity,
            "profit": end_equity - self.start_equity,
            "profit_percent": (end_equity - self.start_equity) / self.start_equity * 100.0,
            "quote_balance": int(balance[quote]),
            "base_balance": balance[base],
            "start_base_balance": self.start_base_balance,
            "end_base_equity": end_base_equity
        }
