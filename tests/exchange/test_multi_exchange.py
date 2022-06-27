import datetime
import random
import time
import numpy

from unittest import TestCase

from tradingkit.cli.runner import Runner
from tradingkit.data.feed.list_feeder import ListFeeder
from tradingkit.exchange.bridge_exchange import BridgeExchange
from tradingkit.exchange.testex import TestEX
from tradingkit.pubsub.core.event import Event
from tradingkit.pubsub.event.book import Book
from tradingkit.pubsub.event.order import Order
from tradingkit.pubsub.event.trade import Trade
from tradingkit.strategy.strategy import Strategy
import copy


class TestTestexMultipleInstances(TestCase):

    def test_events_sync(self):
        symbol = 'BTC/EUR'

        class TestStrategy(Strategy):
            order = None
            exchanges = None
            started_exchanges = {}
            last_event = None

            def set_exchanges(self, exchanges):
                self.exchanges = exchanges

            def get_symbol(self):
                return symbol

            def subscribed_events(self) -> list:
                return [Trade, Order, Book]

            def on_event(self, event):
                # require receive at least on event for exchange before start
                if self.is_started:
                    self.state = self
                else:
                    self.started_exchanges[event.payload['exchange']] = True
                    if len(self.started_exchanges) == len(self.exchanges):
                        self.is_started = True
                        self.start()

                if self.last_event is not None:
                    assert self.last_event.payload['timestamp'] <= event.payload['timestamp']
                self.last_event = event

            def finish(self):
                return {}

        exchange = TestEX({
            'balance': {'EUR': 100000, 'BTC': 0},
            'fees': {
                'maker': 0,
                'taker': 0
            }
        })
        bridge = BridgeExchange(exchange)
        timestamp = time.time() * 1000
        feeder = ListFeeder(
            [{
                'symbol': symbol,
                'timestamp': timestamp + x * 1000,
                'type': 'limit',
                'side': random.choice(['buy', 'sell']),
                'price': x,
                'cost': x,
                'amount': 1,
                'exchange': 'kraken1'
            } for x in range(1, 100)]
        )
        feeder2 = ListFeeder(
            [{
                'symbol': symbol,
                'timestamp': timestamp + x * 1000,
                'type': 'limit',
                'side': random.choice(['buy', 'sell']),
                'price': x,
                'cost': x,
                'amount': 1,
                'exchange': 'kraken2'
            } for x in range(1, 100)]
        )
        exchange2 = copy.deepcopy(exchange)
        bridge2 = BridgeExchange(exchange2)

        plotter = None
        strategy = TestStrategy(bridge, {'symbol': symbol})
        exchange_chains = [{"feeder": feeder, "exchange": exchange, "bridge": bridge, 'name': 'kraken1'},
                           {"feeder": feeder2, "exchange": exchange2, "bridge": bridge2, 'name': 'kraken2'}]
        Runner.run(exchange_chains, plotter, strategy, {'--stats': False, '--optimize': False})

    def test_match_market_order(self):
        symbol = 'BTC/EUR'

        class TestStrategy(Strategy):
            order = None
            exchanges = None
            started_exchanges = {}
            last_event = None

            def set_exchanges(self, exchanges):
                self.exchanges = exchanges

            def get_symbol(self):
                return symbol

            def subscribed_events(self) -> list:
                return [Trade, Order, Book]

            def on_event(self, event):
                # require receive at least on event for exchange before start
                if self.is_started:
                    self.state = self
                else:
                    self.started_exchanges[event.payload['exchange']] = True
                    if len(self.started_exchanges) == len(self.exchanges):
                        self.is_started = True

                if self.is_started:
                    if isinstance(event, Book):
                        if not self.order:
                            self.order = self.exchanges['kraken1'].create_order(self.get_symbol(), 'market', 'buy', 1)
                            self.exchanges['kraken2'].create_order(self.get_symbol(), 'market', 'buy', 2)
                            assert self.order['status'] == 'closed'
                self.last_event = event

            def finish(self):
                return {}

        exchange = TestEX({
            'balance': {'EUR': 100000, 'BTC': 0},
            'fees': {
                'maker': 0,
                'taker': 0
            }
        })
        bridge = BridgeExchange(exchange)
        timestamp = time.time() * 1000
        feeder = ListFeeder(
            [{
                'symbol': symbol,
                'timestamp': timestamp + x * 1000,
                'type': 'limit',
                'side': random.choice(['buy', 'sell']),
                'price': x,
                'cost': x,
                'amount': 1,
                'exchange': 'kraken1'
            } for x in range(1, 100)]
        )
        feeder2 = ListFeeder(
            [{
                'symbol': symbol,
                'timestamp': timestamp + x * 1000,
                'type': 'limit',
                'side': random.choice(['buy', 'sell']),
                'price': x,
                'cost': x,
                'amount': 1,
                'exchange': 'kraken2'
            } for x in range(1, 100)]
        )
        exchange2 = copy.deepcopy(exchange)
        bridge2 = BridgeExchange(exchange2)

        plotter = None
        strategy = TestStrategy(bridge, {'symbol': symbol})
        exchange_chains = [{"feeder": feeder, "exchange": exchange, "bridge": bridge, 'name': 'kraken1'},
                           {"feeder": feeder2, "exchange": exchange2, "bridge": bridge2, 'name': 'kraken2'}]
        Runner.run(exchange_chains, plotter, strategy, {'--stats': False, '--optimize': False})
        assert strategy.exchanges['kraken1'].fetch_balance()['total']['BTC'] == exchange.fetch_balance()['total']['BTC'] == 1
        assert strategy.exchanges['kraken1'].fetch_balance()['total']['EUR'] == exchange.fetch_balance()['total']['EUR'] == 99999
        assert strategy.exchanges['kraken2'].fetch_balance()['total']['BTC'] == exchange2.fetch_balance()['total']['BTC'] == 2
        assert strategy.exchanges['kraken2'].fetch_balance()['total']['EUR'] == exchange2.fetch_balance()['total']['EUR'] == 99998
