from datetime import datetime

from ccxt import Exchange

from tradingkit.pubsub.core.event import Event
from tradingkit.pubsub.core.publisher import Publisher
from tradingkit.pubsub.event.book import Book
from tradingkit.pubsub.core.subscriber import Subscriber
from tradingkit.pubsub.event.candle import Candle
from tradingkit.pubsub.event.funding import Funding
from tradingkit.pubsub.event.open_order import OpenOrder
from tradingkit.pubsub.event.order import Order
from tradingkit.pubsub.event.plot import Plot
from tradingkit.pubsub.event.trade import Trade
from tradingkit.pubsub.event.liquidation import Liquidation


class BridgeExchange(Publisher, Subscriber, Exchange):

    def __init__(self, exchange: Exchange):
        super().__init__()
        self.exchange = exchange
        self.closed_orders = {}
        self.orders_history = {}
        self.last_price = None
        self.has_position = True if "bitmex" in str(exchange.__class__) else False
        exchange.seconds()

    def sec(self):
        return self.exchange.sec()

    def msec(self):
        return self.exchange.msec()

    def usec(self):
        return self.exchange.usec()

    def seconds(self):
        return self.exchange.seconds()

    def milliseconds(self):
        return self.exchange.milliseconds()

    def microseconds(self):
        return self.exchange.microseconds()

    def subscribed_events(self) -> list:
        return [Order, Trade, Book, Candle, Liquidation, Funding, OpenOrder]

    def get_order_asset(self, symbol):
        base, quote = symbol.split('/')
        return quote if self.is_bitmex() else base

    def is_bitmex(self):
        exchange_name = str(self.exchange.__class__.__name__).lower()
        return "bitmex" in exchange_name

    def is_inverse(self, symbol):
        return self.is_bitmex()

    def max_leverage(self, symbol=None):
        return 100 if self.is_bitmex() else 1

    def on_event(self, event: Event):
        if isinstance(event, Book):
            if self.last_price is None:
                self.plot_balances(event.payload['timestamp'], event.payload['symbol'], event.payload['bids'][0][0])
            self.last_price = event.payload['bids'][0][0]
        if isinstance(event, Candle):
            self.plot_candle(event)
        if isinstance(event, Order):
            order = event.payload.copy()
            if order['id'] in self.orders_history.keys():
                self.orders_history[order['id']].update(order)
            event.payload = self.orders_history[order['id']]
            self.plot_order(event)
            self.plot_balances(order['lastTradeTimestamp'], order['symbol'], self.last_price)
        if isinstance(event, OpenOrder):
            self.plot_order(event)
        if isinstance(event, Liquidation):
            trade = event.payload
            self.plot_balances(trade['timestamp'], trade['symbol'], trade['price'])
        self.dispatch(event)

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        return self.exchange.fetch_open_orders(symbol, since, limit, params)

    def create_order(self, symbol, type, amount, side=None, price=None, params={}):
        if amount == 0:
            raise ValueError("Zero order amount is not allowed!!!")
        elif amount < 0 and side is not None:
            raise ValueError("Negative order amount is not allowed!!!")
        if side is None:
            side = "buy" if amount > 0 else "sell"
            if amount < 0:
                amount = -amount
        order = self.exchange.create_order(symbol, type, side, amount, price, params)
        self.orders_history[order['id']] = order
        return order

    def cancel_order(self, order_id, symbol=None, params={}):
        return self.exchange.cancel_order(order_id, symbol, params)

    def match_order(self, trade, order, price, base, quote):
        return self.exchange.match_order(trade, order, price, base, quote)

    def fetch_ticker(self, symbol, **kwargs):
        return self.exchange.fetch_ticker(symbol)

    def private_get_position(self):
        if self.has_position:
            position = self.exchange.private_get_position()
            if not position:
                return [{"currentQty": 0,
                         "homeNotional": 0,
                         "avgEntryPrice": 0,
                         "liquidationPrice": None,
                         "openOrderBuyQty": None,
                         "openOrderSellQty": None,
                         "lastPrice": None,
                         "markPrice": None
                         }]
            else:
                return position
        else:
            raise ValueError("Position not implemented only bitmex !!!")

    def fetch_balance(self):
        return self.exchange.fetch_balance()

    def fetch_free_balance(self):
        return self.exchange.fetch_free_balance()

    def fetch_used_balance(self):
        return self.exchange.fetch_used_balance()

    def fetch_total_balance(self):
        return self.exchange.fetch_total_balance()

    def fetchMarkets(self):
        return self.exchange.fetchMarkets()

    def plot_balances(self, timestamp, symbol, price):
        balances = self.fetch_balance()['total']
        exchange_date = datetime.fromtimestamp(timestamp / 1000.0).isoformat()
        base, quote = symbol.split('/')

        base_balance = balances[base] if base in balances else 0
        quote_balance = balances[quote] if quote in balances else 0

        equity = quote_balance + base_balance * price
        base_equity = base_balance + quote_balance / price
        if self.has_position:
            position = self.private_get_position()[0]
            position_vol = position['currentQty']
            position_price = position['avgEntryPrice']

        else:
            position_vol = base_balance * price
            position_price = 0
        ttip = "<b>Total: %.2f %s</b><br />Quote: %.2f %s<br />Base: %.2f %s (in %s)" % (
            equity, quote,
            quote_balance, quote,
            base_balance * price, quote, base
        )
        self.dispatch(Plot({
            'name': 'Equity',
            'type': 'scatter',
            'mode': 'lines',
            'color': 'blue',
            'yaxis': 'balance',
            'quote': quote,
            'base': base,
            'data': {
                'x': exchange_date,
                'y': equity,
                'base_equity': base_equity,
                'base_balance': base_balance,
                'quote_balance': quote_balance,
                'position_vol': position_vol,
                'position_price': position_price,
                'invested': base_balance * price,
                'tooltip': ttip
            },
        }))

    def plot_order(self, event):
        order = event.payload
        name = None
        if order['status'].lower() == 'filled':
            fill_date = datetime.fromtimestamp(order['lastTradeTimestamp'] / 1000.0).isoformat()
            name = 'buy' if order['side'] == 'buy' else 'sell'
        else:
            fill_date = datetime.fromtimestamp(order['timestamp'] / 1000.0).isoformat()
            if order['status'].lower() == 'open':
                name = 'open_buy' if order['side'] == 'buy' else 'open_sell'
            elif order['status'].lower() == 'canceled':
                name = 'cancel_buy' if order['side'] == 'buy' else 'cancel_sell'
        if name:
            self.dispatch(Plot({
                'name': name,
                'type': 'scatter',
                'mode': 'markers',
                'color': 'green' if order['side'] == 'buy' else 'red',
                'yaxis': 'price',
                'data': {
                    'x': fill_date,
                    'y': order['price'],
                    'type': order['type'],
                    'id': order['id'],
                    'tooltip': "%.4f@%.2f" % (
                        order['amount'] if order['side'] == 'buy' else -order['amount'],
                        order['price']
                    )
                },
            }))

    def plot_candle(self, event):
        candle = event.payload
        candle['liquidationPrice'] = self.private_get_position()[0]['liquidationPrice'] if self.has_position else None
        self.dispatch(Plot({
            'name': 'Price',
            'type': 'candlestick',
            'yaxis': 'price',
            'data': candle,
        }))
