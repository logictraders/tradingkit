import random
from unittest import TestCase

from tradingkit.cli.runner import Runner
from tradingkit.data.feed.list_feeder import ListFeeder
from tradingkit.display.none_plotter import NonePlotter
from tradingkit.display.plotly_plotter import PlotlyPlotter
from tradingkit.exchange.bitmex_backtest import BitmexBacktest
from tradingkit.exchange.bridge_exchange import BridgeExchange
from tradingkit.exchange.testex import TestEX
from tradingkit.pubsub.core.event import Event
from tradingkit.pubsub.event.book import Book
from tradingkit.pubsub.event.order import Order
from tradingkit.pubsub.event.trade import Trade
from tradingkit.strategy.strategy import Strategy


class TestBitmexBacktest(TestCase):

    def test_match_market_order(self):
        symbol = 'BTC/USD'

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

        exchange = BitmexBacktest({
            'balance': {'USD': 100000, 'BTC': 0},
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
        symbol = 'BTC/USD'

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
                        assert balance['BTC'] == self.initial_balance['BTC'] - order['amount'] / order['price'] * 0.00075

            def finish(self):
                return {}

        exchange = BitmexBacktest({
            'balance': {'USD': 100000, 'BTC': 0},
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
        symbol = 'BTC/USD'

        class TestStrategy(Strategy):
            maker_order = None
            initial_balance = None
            after_order_fee_balance = None
            order_amount = 10
            order_price = 500

            def get_symbol(self):
                return symbol

            def subscribed_events(self) -> list:
                return [Trade, Order, Book]

            def start(self):
                self.initial_balance = self.exchange.fetch_balance()['total']
                self.maker_order = self.exchange.create_order(self.get_symbol(), 'limit', 'buy', self.order_amount, self.order_price)

            def on_event(self, event: Event):
                super().on_event(event)
                if isinstance(event, Order):
                    order = event.payload
                    if order['id'] == self.maker_order['id']:
                        self.after_order_fee_balance = self.exchange.fetch_balance()['total']
                        assert self.after_order_fee_balance['BTC'] == \
                               self.initial_balance['BTC'] - order['amount'] / self.order_price * -0.00025

            def finish(self):
                balance = self.exchange.fetch_balance()
                price = self.exchange.fetch_ticker(self.get_symbol())['bid']
                pnl = (self.order_amount * (price / self.order_price) - self.order_amount) / price
                # test profit and loss
                assert balance['free']['BTC'] == self.after_order_fee_balance['BTC'] + pnl
                return {}

        exchange = BitmexBacktest({
            'balance': {'USD': 100000, 'BTC': 0},
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
