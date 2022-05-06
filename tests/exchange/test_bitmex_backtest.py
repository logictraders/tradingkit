import random
import time
from unittest import TestCase

import numpy
from ccxt import InsufficientFunds

from tradingkit.cli.runner import Runner
from tradingkit.data.feed.list_feeder import ListFeeder
from tradingkit.display.none_plotter import NonePlotter
from tradingkit.display.plotly_plotter import PlotlyPlotter
from tradingkit.exchange.bitmex_backtest import BitmexBacktest
from tradingkit.exchange.bridge_exchange import BridgeExchange
from tradingkit.exchange.testex import TestEX
from tradingkit.pubsub.core.event import Event
from tradingkit.pubsub.event.book import Book
from tradingkit.pubsub.event.liquidation import Liquidation
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
            'balance': {'USD': 0, 'BTC': 100},
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
        plotter = None
        strategy = TestStrategy(bridge, {'symbol': symbol})
        exchange_chains = [{"feeder": feeder, "exchange": exchange, "bridge": bridge}]
        Runner.run(exchange_chains, plotter, strategy, {'--stats': False, '--optimize': False})

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
            'balance': {'USD': 0, 'BTC': 100},
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
        plotter = None
        strategy = TestStrategy(bridge, {'symbol': symbol})
        exchange_chains = [{"feeder": feeder, "exchange": exchange, "bridge": bridge}]
        Runner.run(exchange_chains, plotter, strategy, {'--stats': False, '--optimize': False})

    def test_maker_fees_and_pln(self):
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
                pnl = (1 / self.order_price - 1 / price) * self.order_amount
                # test profit and loss
                assert balance['free']['BTC'] == self.after_order_fee_balance['BTC'] + pnl
                return {}

        exchange = BitmexBacktest({
            'balance': {'USD': 0, 'BTC': 100},
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
        plotter = None
        strategy = TestStrategy(bridge, {'symbol': symbol})
        exchange_chains = [{"feeder": feeder, "exchange": exchange, "bridge": bridge}]
        Runner.run(exchange_chains, plotter, strategy, {'--stats': False, '--optimize': False})

    def test_liqudation_price(self):
        symbol = 'BTC/USD'

        class TestStrategy(Strategy):
            maker_order = None
            initial_balance = None
            after_order_fee_balance = None
            order_amount = 10000
            order_price = 500

            def get_symbol(self):
                return symbol

            def subscribed_events(self) -> list:
                return [Trade, Order, Liquidation]

            def start(self):
                self.initial_balance = self.exchange.fetch_balance()['total']
                self.maker_order = \
                    self.exchange.create_order(self.get_symbol(), 'limit', 'buy', self.order_amount, self.order_price)

            def on_event(self, event: Event):
                super().on_event(event)
                if isinstance(event, Order):
                    order = event.payload
                    if order['id'] == self.maker_order['id']:
                        self.after_order_fee_balance = self.exchange.fetch_balance()['total']
                        assert self.after_order_fee_balance['BTC'] == \
                               self.initial_balance['BTC'] - order['amount'] / self.order_price * -0.00025

                if isinstance(event, Liquidation):
                    previous_trade_price_pnl = (1 / self.order_price - 1 / (event.payload['price'] + 1)) * self.order_amount
                    pnl = (1 / self.order_price - 1 / event.payload['price']) * self.order_amount

                    # test if liquidation event is dispatched just when balance is equal or below 0 not before
                    assert self.after_order_fee_balance['BTC'] + pnl <= 0 and \
                           self.after_order_fee_balance['BTC'] + previous_trade_price_pnl > 0

            def finish(self):
                return {}

        exchange = BitmexBacktest({
            'balance': {'USD': 0, 'BTC': 100},
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
            } for x in range(1000, 1, -1)]
        )
        plotter = None
        strategy = TestStrategy(bridge, {'symbol': symbol})
        exchange_chains = [{"feeder": feeder, "exchange": exchange, "bridge": bridge}]
        self.assertRaises(InsufficientFunds, Runner.run, exchange_chains, plotter, strategy, {'--stats': False, '--optimize': False})

    def test_max_draw_dawn(self):
        symbol = 'BTC/USD'
        initial_balance = 100
        order_price = 500
        order_amount = initial_balance * order_price

        class TestStrategy(Strategy):
            maker_order = None

            def get_symbol(self):
                return symbol

            def subscribed_events(self) -> list:
                return [Trade, Order, Liquidation]

            def start(self):
                initial_balance = self.exchange.fetch_balance()['total']
                self.maker_order = \
                    self.exchange.create_order(self.get_symbol(), 'limit', 'buy', order_amount, order_price)

            def on_event(self, event: Event):
                super().on_event(event)

            def finish(self):
                return {}

        exchange = BitmexBacktest({
            'balance': {'USD': 0, 'BTC': 100},
            'fees': {
                'maker': 0.0,
                'taker': 0.0
            }
        })
        bridge = BridgeExchange(exchange)
        timestamp = time.time()
        feeder = ListFeeder(
            [{
                'symbol': symbol,
                'timestamp':  timestamp + abs(600 - x) * 1000 * 60 * 60 * 24,
                'type': 'limit',
                'side': random.choice(['buy', 'sell']),
                'price': x,
                'cost': x,
                'amount': 1
            } for x in range(501, 399, -1)]
        )
        plotter = None
        strategy = TestStrategy(bridge, {'symbol': symbol})
        exchange_chains = [{"feeder": feeder, "exchange": exchange, "bridge": bridge}]
        result = Runner.run(exchange_chains, plotter, strategy, {'--stats': True, '--optimize': False})

        assert result['max_drawdown'] == (exchange.fetch_balance()['free']['BTC'] - initial_balance) / initial_balance

    def test_sharpe_ratio(self):
        symbol = 'BTC/USD'
        initial_balance = 100
        order_price = 100
        order_amount = initial_balance * order_price

        class TestStrategy(Strategy):
            maker_order = None

            def get_symbol(self):
                return symbol

            def subscribed_events(self) -> list:
                return [Trade, Order, Liquidation]

            def start(self):
                initial_balance = self.exchange.fetch_balance()['total']

            def on_event(self, event: Event):
                super().on_event(event)
                if isinstance(event, Trade):
                    if event.payload['price'] > 100 and self.maker_order is None:
                        self.maker_order = \
                            self.exchange.create_order(self.get_symbol(), 'market', 'buy', order_amount)

            def finish(self):
                return {}

        exchange = BitmexBacktest({
            'balance': {'USD': 0, 'BTC': 100},
            'fees': {
                'maker': 0.0,
                'taker': 0.0
            }
        })
        bridge = BridgeExchange(exchange)
        timestamp = time.time() * 1000
        feeder = ListFeeder(
            [{
                'symbol': symbol,
                'timestamp':  timestamp + x * 1000 * 60 * 60 * 24,
                'type': 'limit',
                'side': random.choice(['buy', 'sell']),
                'price': x,
                'cost': x,
                'amount': 1
            } for x in range(99, 103)]
        )
        plotter = None
        strategy = TestStrategy(bridge, {'symbol': symbol})
        exchange_chains = [{"feeder": feeder, "exchange": exchange, "bridge": bridge}]
        result = Runner.run(exchange_chains, plotter, strategy, {'--stats': True, '--optimize': False})


        days_runing = 2
        eq1 = initial_balance + (1/100 - 1/101) * order_amount
        eq2 = initial_balance + (1/100 - 1/102) * order_amount
        partial_profits = [(eq1/100 -1) * 100, (eq2/100 -1) * 100]
        standard_deviation = numpy.std(partial_profits)
        total_profit = partial_profits[-1]
        anual_profit = total_profit / days_runing * 365
        zero_risk_profit = 5
        expected_sharpe_ratio = (anual_profit - zero_risk_profit) / standard_deviation

        assert result['sharpe_ratio'] == expected_sharpe_ratio