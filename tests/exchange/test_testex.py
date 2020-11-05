import random
from unittest import TestCase

from tradingkit.cli.runner import Runner
from tradingkit.data.feed.list_feeder import ListFeeder
from tradingkit.display.none_plotter import NonePlotter
from tradingkit.display.plotly_plotter import PlotlyPlotter
from tradingkit.exchange.bridge_exchange import BridgeExchange
from tradingkit.exchange.testex import TestEX
from tradingkit.pubsub.core.event import Event
from tradingkit.pubsub.event.book import Book
from tradingkit.pubsub.event.order import Order
from tradingkit.pubsub.event.trade import Trade
from tradingkit.strategy.strategy import Strategy


class TestTestex(TestCase):

    def test_match_market_order(self):
        symbol = 'BTC/EUR'

        class TestStrategy(Strategy):
            order = None

            def get_symbol(self):
                return symbol

            def subscribed_events(self) -> list:
                return [Trade, Order, Book]

            def on_event(self, event: Event):
                super().on_event(event)
                if isinstance(event, Book):
                    if not self.order:
                        self.order = self.exchange.create_order(self.get_symbol(), 'market', 'buy', 1)
                        assert self.order['status'] == 'closed'

                if isinstance(event, Order):
                    order = event.payload
                    assert order['id'] == self.order['id']

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
        plotter = NonePlotter()
        strategy = TestStrategy(bridge, {'symbol': symbol})

        Runner.run(feeder, exchange, plotter, strategy, bridge)

    def test_taker_fees(self):
        symbol = 'BTC/EUR'

        class TestStrategy(Strategy):
            taker_order = None
            initial_balance = None

            def get_symbol(self):
                return symbol

            def subscribed_events(self) -> list:
                return [Trade, Order, Book]

            def start(self):
                self.initial_balance = self.exchange.fetch_balance()['total']
                self.taker_order = self.exchange.create_order(self.get_symbol(), 'market', 'buy', 1)

            def on_event(self, event: Event):
                super().on_event(event)
                if isinstance(event, Order):
                    order = event.payload
                    if order['id'] == self.taker_order['id']:
                        balance = self.exchange.fetch_balance()['total']
                        assert balance['BTC'] == 1
                        assert balance['EUR'] == self.initial_balance['EUR'] - order['price'] * 1.00075

            def finish(self):
                return {}

        exchange = TestEX({
            'balance': {'EUR': 100000, 'BTC': 0},
            'fees': {
                'maker': -0.00025,
                'taker': 0.00075
            }
        })
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
        plotter = NonePlotter()
        strategy = TestStrategy(bridge, {'symbol': symbol})

        Runner.run(feeder, exchange, plotter, strategy, bridge)

    def test_maker_fees(self):
        symbol = 'BTC/EUR'

        class TestStrategy(Strategy):
            maker_order = None
            initial_balance = None

            def get_symbol(self):
                return symbol

            def subscribed_events(self) -> list:
                return [Trade, Order, Book]

            def start(self):
                self.initial_balance = self.exchange.fetch_balance()['total']
                self.maker_order = self.exchange.create_order(self.get_symbol(), 'limit', 'buy', 1, 500)

            def on_event(self, event: Event):
                super().on_event(event)
                if isinstance(event, Order):
                    order = event.payload
                    if order['id'] == self.maker_order['id']:
                        balance = self.exchange.fetch_balance()['total']
                        assert balance['BTC'] == 1
                        assert balance['EUR'] == self.initial_balance['EUR'] - order['price'] * (1 - 0.00025)

            def finish(self):
                return {}

        exchange = TestEX({
            'balance': {'EUR': 100000, 'BTC': 0},
            'fees': {
                'maker': -0.00025,
                'taker': 0.00075
            }
        })
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
        plotter = NonePlotter()
        strategy = TestStrategy(bridge, {'symbol': symbol})

        Runner.run(feeder, exchange, plotter, strategy, bridge)

    def test_simple_one_percent_strategy(self):
        symbol = 'BTC/EUR'

        class TestStrategy(Strategy):
            order = None

            def get_symbol(self):
                return symbol

            def subscribed_events(self) -> list:
                return [Trade, Order, Book]

            def start(self):
                for i in range(150, 200):
                    self.order = self.exchange.create_order(
                        symbol=self.get_symbol(),
                        type='limit',
                        side='buy',
                        amount=1,
                        price=i
                    )

            def on_event(self, event: Event):
                super().on_event(event)
                if isinstance(event, Order):
                    order = event.payload
                    if order['status'] == 'filled' and order['side'] == 'buy':
                        self.order = self.exchange.create_order(
                            symbol=self.get_symbol(),
                            type='limit',
                            side='sell',
                            amount=1,
                            price=order['price'] * 1.01
                        )

            def finish(self):
                balance = self.exchange.fetch_balance()['total']
                assert balance['BTC'] == 0
                assert balance['EUR'] == 100000 + sum([x * 0.01 for x in range(150, 200)])
                return {}

        exchange = TestEX({
            'balance': {'EUR': 100000, 'BTC': 0},
            'fees': {
                'maker': 0,
                'taker': 0
            }
        })
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
            } for x in (list(range(1000, 100)) + list(range(100, 1000)))]
        )
        plotter = PlotlyPlotter()
        strategy = TestStrategy(bridge, {'symbol': symbol})

        Runner.run(feeder, exchange, plotter, strategy, bridge)


