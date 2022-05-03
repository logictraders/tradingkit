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
        self.start_equity = 0
        self.is_started = False
        self.start_base_balance = 0
        self.start_base_equity = 0

    @abstractmethod
    def get_symbol(self):
        pass

    def start(self):
        logging.info("Start strategy %s" % str(self.__class__))
        if hasattr(self, 'exchanges'):
            for exchange in self.exchanges.keys():
                _, base_balance, start_base_equity, start_equity = self.get_exchange_balance(
                    self.exchanges[exchange].exchange, self.config['symbol'])
                self.start_equity += start_equity
                self.start_base_equity += start_base_equity
                self.start_base_balance += base_balance

        else:
            _, base_balance, start_base_equity, start_equity = self.get_exchange_balance(self.exchange,
                                                                                      self.config['symbol'])

            self.start_equity = start_equity
            self.start_base_equity = start_base_equity
            self.start_base_balance = base_balance

        logging.info("Initial Equity: %s" % str(self.start_equity))

    def get_exchange_balance(self, exchange, symbol):
        balance = exchange.fetch_balance()['total']
        base, quote = symbol.split('/')
        quote_balance = balance[quote] if quote in balance else 0
        base_balance = balance[base] if base in balance else 0
        equity = quote_balance + base_balance * exchange.fetch_ticker(symbol)['bid']
        base_equity = quote_balance / exchange.fetch_ticker(symbol)['bid'] + base_balance
        return quote_balance, base_balance, base_equity, equity

    def on_event(self, event: Event):
        if not self.is_started:
            self.is_started = True
            self.start()

    def finish(self):
        logging.info("Finish strategy %s" % str(self.__class__))
        if hasattr(self, 'exchanges'):
            quote_balance = base_balance = end_base_equity = end_equity = 0
            for exchange in self.exchanges.keys():
                _quote_balance, _base_balance, _end_base_equity, _end_equity = self.get_exchange_balance(
                    self.exchanges[exchange].exchange, self.config['symbol'])
                if self.exchange.has_position:
                    position = self.exchange.private_get_position()[0]
                    pnl = (price / position['avgEntryPrice'] - 1) * position['currentQty']
                    _end_equity += pnl

                quote_balance += _quote_balance
                base_balance += _base_balance
                end_base_equity += _end_base_equity
                end_equity += _end_equity

        else:
            quote_balance, base_balance, end_base_equity, end_equity = self.get_exchange_balance(self.exchange,
                                                                                      self.config['symbol'])
            if self.exchange.has_position:
                position = self.exchange.private_get_position()[0]
                pnl = (price / position['avgEntryPrice'] - 1) * position['currentQty']
                end_equity += pnl

        logging.info("Equity: %.2f EUR" % end_equity)

        return {
            "start_equity": self.start_equity,
            "end_equity": end_equity,
            "profit": end_equity - self.start_equity,
            "profit_percent": (end_equity - self.start_equity) / self.start_equity * 100.0,
            "quote_balance": int(quote_balance),
            "base_balance": base_balance,
            "start_base_balance": self.start_base_balance,
            "end_base_equity": end_base_equity
        }
