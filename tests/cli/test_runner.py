import random
from unittest import TestCase

from ccxt import InsufficientFunds

from tradingkit.cli.runner import Runner
from tradingkit.data.feed.list_feeder import ListFeeder
from tradingkit.display.highstock.highstock_plotter import HighstockPlotter
from tradingkit.display.none_plotter import NonePlotter
from tradingkit.exchange.bridge_exchange import BridgeExchange
from tradingkit.exchange.testex import TestEX
from tradingkit.pubsub.core.event import Event
from tradingkit.pubsub.event.book import Book
from tradingkit.pubsub.event.order import Order
from tradingkit.pubsub.event.trade import Trade
from tradingkit.strategy.strategy import Strategy


class TestRunner(TestCase):

    def test_insufficient_funds(self):
        symbol = 'BTC/EUR'

        class TestStrategy(Strategy):
            def get_symbol(self):
                return symbol

            def subscribed_events(self) -> list:
                return [Trade, Order, Book]

            def on_event(self, event: Event):
                super().on_event(event)
                self.exchange.create_order(self.get_symbol(), 'market', 'buy', 1e10)

            def finish(self):
                return {}

        exchange = TestEX()
        bridge = BridgeExchange(exchange)
        feeder = ListFeeder(
            [{
                'symbol': symbol,
                'timestamp': x,
                'type': 'limit',
                'side': random.choice(['buy', 'sell']),
                'price': x,
                'cost': x,
                'amount': 1
            } for x in range(100, 1000)]
        )
        plotter = HighstockPlotter()
        strategy = TestStrategy(bridge, {'symbol': symbol})

        self.assertRaises(InsufficientFunds, Runner.run, feeder, plotter, strategy, {'--stats': False, '--optimize': False})


