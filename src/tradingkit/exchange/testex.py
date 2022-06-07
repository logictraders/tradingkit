import logging
import uuid
from datetime import datetime

from ccxt import Exchange, OrderNotFound, InsufficientFunds

from tradingkit.pubsub.core.event import Event
from tradingkit.pubsub.core.publisher import Publisher
from tradingkit.pubsub.event.book import Book
from tradingkit.pubsub.core.subscriber import Subscriber
from tradingkit.pubsub.event.candle import Candle
from tradingkit.pubsub.event.open_order import OpenOrder
from tradingkit.pubsub.event.order import Order
from tradingkit.pubsub.event.plot import Plot
from tradingkit.pubsub.event.trade import Trade
from tradingkit.pubsub.event.funding import Funding


class TestEX(Publisher, Subscriber, Exchange):

    def __init__(self, params=None):
        super().__init__()
        if params is None:
            params = {
                'balance': {'EUR': 100000, 'BTC': 0},
                'fees': {
                    'maker': 0.002,
                    'taker': 0.002
                }
            }
        self.fees = params['fees'].copy()
        self.balance = params['balance'].copy()
        self.initial = params['balance'].copy()

        self.open_orders = {}
        self.history = []
        self.orderbooks = {}
        self.orders_scheduled_to_close = []
        self.max_invested = 0
        self.ready = False
        self.undispatched_orders = []
        self.name = 'kraken'

        # timestamp in milliseconds
        self.timestamp = 0

    def set_name(self, name):
        self.name = name

    def sec(self):
        return self.seconds()

    def msec(self):
        return self.milliseconds()

    def usec(self):
        return self.microseconds()

    def seconds(self):
        return self.milliseconds() / 1000

    def milliseconds(self):
        return self.timestamp

    def microseconds(self):
        return self.milliseconds() * 1000

    def sleep(self, milliseconds):
        raise NotImplementedError("sleep() not implemented yet.")

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        return list(self.open_orders.values())

    def fetch_closed_orders(self, symbol=None, since=None, limit=None, params={}):
        return self.history

    def fetch_order(self, id, symbol=None, params={}):
        if id in self.open_orders.keys():
            return self.open_orders[id]
        else:
            for order in self.history:
                if order['id'] == id:
                    return order
        return None

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        order_id = str(uuid.uuid4())
        now = self.milliseconds()
        order = {
            'id': order_id,
            'timestamp': now,
            'datetime': datetime.fromtimestamp(self.seconds()).isoformat(),
            'status': 'closed' if type == 'market' else 'open',
            'symbol': symbol,
            'type': type,
            'side': side,
            'amount': amount,
            'price': price,
            'params': params
        }
        logging.debug("%s::create_order(%s)" % (self.__class__.__name__, order))
        if not self.funds_enough(order):
            raise InsufficientFunds("No funds enough: balance: %s, order: %s" % (str(self.balance), str(order)))
        self.open_orders[order_id] = order
        if type == 'market':
            base, quote = symbol.split('/')
            _price = self.orderbooks[symbol]['bids'][0][0]
            self.match_order({"price": _price, 'timestamp': now}, order, _price, base, quote)
            self.clean_orders()
        if order['status'] == 'filled':
            order['status'] = 'closed'
        else:
            self.dispatch(OpenOrder(order))
        return order

    def cancel_order(self, order_id, symbol=None, params={}):
        logging.debug("%s::cancel_order(%s)" % (self.__class__.__name__, order_id))
        if order_id in self.open_orders:
            order = self.open_orders[order_id]
            del self.open_orders[order_id]
            order['status'] = 'canceled'
            order['timestamp'] = self.milliseconds()
            self.dispatch(OpenOrder(order))
        else:
            raise OrderNotFound("Cannot cancel order: not found")

    def subscribed_events(self) -> list:
        return [Order, Trade, Book, Candle, Funding]

    def on_event(self, event: Event):
        if event.payload['exchange'] == self.name:
            self.dispatch(event)
            if isinstance(event, Trade):
                trade = event.payload
                self.timestamp = trade['timestamp']
                self.update_order_book(trade)
                symbol = trade['symbol']
                assets = symbol.split('/')
                for asset in assets:
                    if asset not in self.balance:
                        self.balance[asset] = 0
                base, quote = assets
                self.plot_balances(base, quote, trade['price'])
                for order_id in self.open_orders:
                    order = self.open_orders[order_id]
                    if order['symbol'] == symbol:
                        price = trade['price'] if order['type'] == 'market' else order['price']
                        self.match_order(trade, order, price, base, quote)
                for order in self.undispatched_orders:
                    self.dispatch(Order(order))
                self.undispatched_orders = []
                self.clean_orders()
                self.ready = True
                book = self.orderbooks[symbol].copy()
                book['symbol'] = symbol
                self.dispatch(Book(book))


    def dispatch(self, event: Event):
        # prevent from dispatching events if the exchange is not ready
        if self.ready:
            event.payload['exchange'] = self.name
            super().dispatch(event)

    def update_order_book(self, trade):
        symbol = trade['symbol']
        if symbol not in self.orderbooks:
            self.orderbooks[symbol] = {'bids': [], 'asks': []}
        self.orderbooks[symbol]['asks'] = [[trade['price'], trade['amount']]]
        self.orderbooks[symbol]['bids'] = [[trade['price'], trade['amount']]]
        self.orderbooks[symbol]['timestamp'] = trade['timestamp']

    def match_order(self, trade, order, price, base, quote):
        taker_or_maker = 'maker' if order['type'] == 'limit' else 'taker'
        fee = self.fees[taker_or_maker]
        if order['side'] == 'buy':
            if order['type'] == 'stop':
                if price <= trade['price']:
                    self.balance[quote] -= order['amount'] * price * (1 + fee)
                    self.balance[base] += order['amount']
                    order['status'] = 'filled'
            elif price >= trade['price']:
                self.balance[quote] -= order['amount'] * price * (1 + fee)
                self.balance[base] += order['amount']
                order['status'] = 'filled'
        else:
            if order['type'] == 'stop':
                if price >= trade['price']:
                    self.balance[base] -= order['amount']
                    self.balance[quote] += order['amount'] * price * (1 - fee)
                    order['status'] = 'filled'
            elif price <= trade['price']:
                self.balance[base] -= order['amount']
                self.balance[quote] += order['amount'] * price * (1 - fee)
                order['status'] = 'filled'
        if order['status'] == 'filled':
            order['lastTradeTimestamp'] = trade['timestamp']
            if order['price'] is None:
                order['price'] = price
            self.orders_scheduled_to_close.append(order)

    def fetch_l2_order_book(self, symbol, limit=None, params={}):
        return self.orderbooks[symbol]

    def clean_orders(self):
        orders_to_dispatch = []
        for order in self.orders_scheduled_to_close:
            del self.open_orders[order['id']]
            self.history.append(order)
            if order['type'] == 'market':
                self.undispatched_orders.append(order)
            else:
                orders_to_dispatch.append(order)

        self.orders_scheduled_to_close = []

        for order in orders_to_dispatch:
            self.dispatch(Order(order))

    def plot_balances(self, base, quote, price):
        balance = self.balance.copy()
        exchange_date = datetime.fromtimestamp(self.seconds()).isoformat()
        base_value = balance[base] * price
        equity = balance[quote] + base_value
        ttip = "<b>Total: %.2f %s</b><br />Quote: %.2f %s<br />Base: %.2f %s" % (
            equity, quote,
            balance[quote], quote,
            balance[base], base
        )
        self.dispatch(Plot({
            'name': 'Equity',
            'type': 'scatter',
            'mode': 'lines',
            'color': 'blue',
            'yaxis': 'balance',
            'data': {
                'x': exchange_date,
                'y': equity,
                'tooltip': ttip
            },
        }))

    def funds_enough(self, order):
        base, quote = order['symbol'].split('/')
        if order['type'] == 'limit':
            cost = order['amount'] * order['price']
        else:
            book_side = 'bids' if order['side'] == 'sell' else 'asks'
            cost = order['amount'] * self.orderbooks[order['symbol']][book_side][0][0]

        sum_same_side_orders = sum([o['amount'] for o in self.open_orders.values() if o['side'] == order['side']])

        if order['side'] == 'buy':
            return cost + sum_same_side_orders <= self.balance[quote]
        else:
            return order['amount'] + sum_same_side_orders <= self.balance[base]

    def fetch_ticker(self, symbol, **kwargs):
        if symbol in self.orderbooks:
            if not self.orderbooks[symbol]:
                raise KeyError("TestEX is not ready yet")
            return {"bid": self.orderbooks[symbol]['bids'][0][0], "ask": self.orderbooks[symbol]['asks'][0][0], "timestamp": self.milliseconds()}
        raise NotImplementedError("Symbol %s not found in testex.orderbooks" % symbol)

    def fetch_balance(self):
        balances = {}
        free_balance = self.fetch_free_balance()
        balances['free'] = free_balance
        used_balance = self.fetch_used_balance()
        for asset in used_balance.keys():
            balances[asset] = {'free': free_balance[asset], 'used': used_balance[asset], 'total': self.balance[asset]}
        balances['used'] = used_balance
        balances['total'] = self.balance.copy()
        return balances

    def fetch_free_balance(self):
        free_balance = self.balance.copy()
        for key in self.open_orders.keys():
            order = self.open_orders[key]
            side = order['side']
            base, quote = order['symbol'].split('/')
            if side == "buy":
                free_balance[quote] -= order['amount'] * order['price']
            else:
                free_balance[base] -= order['amount']
        return free_balance

    def fetch_used_balance(self):
        free_balance = self.fetch_free_balance()
        used_balance = self.balance.copy()
        for asset in used_balance.keys():
            used_balance[asset] -= free_balance[asset]
        return used_balance

    def fetch_total_balance(self):
        return self.balance.copy()
