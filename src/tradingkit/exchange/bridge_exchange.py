from datetime import datetime, timedelta

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
import numpy


class BridgeExchange(Publisher, Subscriber, Exchange):

    def __init__(self, exchange: Exchange):
        super().__init__()
        self.exchange = exchange
        self.closed_orders = {}
        self.orders_history = {}
        self.balance_history = []
        self.last_balance_check = None
        self.peak_balance = 0
        self.max_drawdown = 0
        self.last_price = None
        self.symbol = None
        self.has_position = True if "bitmex" in str(exchange.__class__) else False
        exchange.seconds()

        self.candles = None
        self.last_candle = None
        self.timeframes = {"1m": 60,
                           "5m": 300,
                           "15m": 900,
                           "30m": 1800,
                           "1H": 3600,
                           "4H": 14400,
                           "6H": 21600,
                           "12H": 43200,
                           "1D": 86400,
                           "2D": 172800,
                           "4D": 345600,
                           "1W": 604800,
                           "2W": 1209600,
                           "1M": 2629800}

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
                self.symbol = event.payload['symbol']
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
            order = event.payload.copy()
            self.plot_balances(order['timestamp'], order['symbol'], self.last_price)
        if isinstance(event, Liquidation):
            trade = event.payload
            self.plot_balances(trade['timestamp'], trade['symbol'], trade['price'])
        if isinstance(event, Trade):
            trade = event.payload
            self.candle_dispatcher(trade)
        self.dispatch(event)

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        return self.exchange.fetch_open_orders(symbol, since, limit, params)

    def create_order(self, symbol, type, side=None, amount=0, price=None, params={}):
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

    def get_max_draw_down(self):
        return self.max_drawdown

    def plot_balances(self, timestamp, symbol, price):
        exchange_date = datetime.fromtimestamp(timestamp / 1000.0).isoformat()
        base, quote = symbol.split('/')
        balances = self.fetch_balance()
        balances = balances['free'] if balances['free'][base] else balances['total']

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
        self.calculate_max_drawdown(base_balance, quote_balance)
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
        date = datetime.fromisoformat(candle['datetime'])
        if self.last_balance_check is None or date - self.last_balance_check > timedelta(hours=1):
            self.last_balance_check = date
            self.balance_history.append(self.save_current_balance(candle['close']))

    def calculate_max_drawdown(self, base_balance, quote_balance, symbol):
        if self.last_price:
            balance = quote_balance + base_balance * self.last_price if quote_balance > 0 else base_balance

            if balance > self.peak_balance:
                self.peak_balance = balance

            drawdown = (balance - self.peak_balance) / self.peak_balance
            self.max_drawdown = min(self.max_drawdown, drawdown)

    def save_current_balance(self, price):
        base, quote = self.symbol.split('/')
        balances = self.fetch_balance()
        balances = balances['free'] if balances['free'][base] else balances['total']

        base_balance = balances[base] if base in balances else 0
        quote_balance = balances[quote] if quote in balances else 0

        # todo use quote equity for kraken (equity = quote_balance + base_balance * price)
        base_equity = base_balance + quote_balance / price
        return base_equity

    def get_sharpe_ratio(self):
        standard_desviation = numpy.std(self.balance_history)
        sharpe_ratio = (self.balance_history[-1] / self.balance_history[0]) / standard_desviation
        return sharpe_ratio

    def candle_dispatcher(self, trade):

        if self.candles is None:
            self.candles = {x:{} for x in self.timeframes.keys()}

        if self.last_candle is None:
            self.last_candle = {x:None for x in self.timeframes.keys()}

        for tf in self.timeframes.keys():
            sec = self.timeframes[tf]
            key = trade['timestamp'] // (sec * 1000) * sec
            key = str(datetime.fromtimestamp(key))
            if self.last_candle[tf] is not None and key in self.candles[tf]:
                self.candles[tf][key]['high'] = max(self.candles[tf][key]['high'], trade['price'])
                self.candles[tf][key]['low'] = min(self.candles[tf][key]['low'], trade['price'])
                self.candles[tf][key]['close'] = trade['price']
                self.candles[tf][key]['vol'] += trade['amount']
                self.candles[tf][key]['cost'] += trade['cost']
                self.candles[tf][key]['trades'] += 1
            else:
                self.candles[tf][key] = {
                    'datetime': key,
                    'open': trade['price'],
                    'high': trade['price'],
                    'low': trade['price'],
                    'close': trade['price'],
                    'vol': trade['amount'],
                    'cost': trade['cost'],
                    'trades': 1,
                    'timeframe': tf
                }
                if self.last_candle[tf] is not None:
                    self.dispatch(Candle(self.last_candle[tf]))
                    self.plot_candle(Candle(self.last_candle[tf]))
            self.last_candle[tf] = self.candles[tf][key]
