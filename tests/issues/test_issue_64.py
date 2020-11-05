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


class TestIssue64(TestCase):
    """
    This test demonstrates the issue #64 malfunction
    see https://github.com/QbitArtifacts/tradingkit/issues/64
    """

    def test_demonstrate(self):
        symbol = 'BTC/EUR'

        class TestStrategy(Strategy):
            order = None
            buy_orders = None
            sell_orders = None
            buys = [
                {"price": 8142.1, "amount": 0.012},
                {"price": 8061.5, "amount": 0.0122},
                {"price": 7981.5, "amount": 0.0246},
                {"price": 7902.5, "amount": 0.0496},
                {"price": 7823.5, "amount": 0.1002},
                {"price": 7745.5, "amount": 0.2024},
            ]
            sells = [
                {"price": 7823.5, "amount": 0.3883},
            ]

            def get_symbol(self):
                return symbol

            def subscribed_events(self) -> list:
                return [Trade, Order, Book]

            def start(self):
                self.buy_orders = {}
                self.sell_orders = {}
                for backlog in self.buys:
                    order = self.exchange.create_order(
                        symbol=self.get_symbol(),
                        type='limit',
                        side='buy',
                        amount=backlog['amount'],
                        price=backlog['price']
                    )
                    self.buy_orders[order['id']] = order

            def on_event(self, event: Event):
                super().on_event(event)
                if isinstance(event, Order):
                    order = event.payload
                    if order['status'] == 'filled':
                        if order['side'] == 'buy':
                            del self.buy_orders[order['id']]
                            if len(self.buy_orders) <= 0:
                                for backlog in self.sells:
                                    order = self.exchange.create_order(
                                        symbol=self.get_symbol(),
                                        type='limit',
                                        side='sell',
                                        amount=backlog['amount'],
                                        price=backlog['price']
                                    )
                                    self.sell_orders[order['id']] = order
                        else:
                            del self.sell_orders[order['id']]

            def finish(self):
                balance = self.exchange.fetch_balance()['total']
                assert round(balance['BTC'], 4) == 0.0127
                assert round(balance['EUR'], 4) == 99901.8967
                return {}

        exchange = TestEX({
            'balance': {'EUR': 100000, 'BTC': 0},
            'fees': {
                'maker': 0.0,
                'taker': 0.0
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
            } for x in (list(range(8200, 7700)) + list(range(7700, 8000)))]
        )
        plotter = PlotlyPlotter()
        strategy = TestStrategy(bridge, {'symbol': symbol})

        Runner.run(feeder, exchange, plotter, strategy, bridge)


