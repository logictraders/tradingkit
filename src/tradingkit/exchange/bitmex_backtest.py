from tradingkit.exchange.testex import TestEX
from datetime import datetime

from tradingkit.pubsub.core.event import Event
from tradingkit.pubsub.event.funding import Funding
from tradingkit.pubsub.event.liquidation import Liquidation
from tradingkit.pubsub.event.plot import Plot
import logging

from tradingkit.pubsub.event.trade import Trade
from ccxt import InsufficientFunds


class BitmexBacktest(TestEX):
    def sleep(self, milliseconds):
        pass

    def __init__(self, params=None):
        super().__init__({'balance': {'USD': 0, 'BTC': 10}, 'fees': {'maker': -0.00025, 'taker': 0.00075}})
        self.position = {"currentQty": 0,  # currentQty
                         "homeNotional": 0,  # homeNotional base value (disabled)
                         "avgEntryPrice": 0,
                         "liquidationPrice": None,
                         "openOrderBuyQty": None,
                         "openOrderSellQty": None,
                         "lastPrice": None,
                         "markPrice": None
                         }
        self.leverage = 100
        self.funding_rate = None

    def match_order(self, trade, order, price, base, quote):
        # TODO:
        #   - partial fills
        fee = self.fees['taker'] if order['type'] == 'market' else self.fees['maker']
        if order['side'] == 'buy':
            if order['type'] == 'stop':
                if price <= trade['price']:
                    self.update_position(order['amount'], trade['price'], base)
                    order['status'] = 'filled'
            elif price >= trade['price']:
                self.update_position(order['amount'], price, base)
                order['status'] = 'filled'
        else:
            if order['type'] == 'stop':
                if price >= trade['price']:
                    self.update_position(-order['amount'], trade['price'], base)
                    order['status'] = 'filled'
            elif price <= trade['price']:
                self.update_position(-order['amount'], price, base)
                order['status'] = 'filled'
        if order['status'] == 'filled':
            order['lastTradeTimestamp'] = trade['timestamp']
            order['price'] = trade['price']
            fee = self.fees['maker'] if order['type'] == 'limit' else self.fees['taker']
            fee_pnl = abs(order['amount']) * fee
            logging.debug("fees apply: %s $" % str(-fee_pnl))
            self.balance[base] -= fee_pnl / price
            self.orders_scheduled_to_close.append(order)
            self.plot_balances(base, quote, price)

    def update_position(self, quote_volume, avg_order_price, base):
        against = quote_volume * self.position['currentQty'] < 0
        if against:
            if abs(self.position['currentQty']) < abs(quote_volume):  # position changes sign, update PNL
                pnl = (avg_order_price / self.position['avgEntryPrice'] - 1) * self.position['currentQty']
                self.balance[base] += pnl / avg_order_price
                self.position['avgEntryPrice'] = avg_order_price

            else:  # decrease position, update PNL
                pnl = (avg_order_price / self.position['avgEntryPrice'] - 1) * abs(quote_volume)
                if self.position['currentQty'] >= 0:
                    self.balance[base] += pnl / avg_order_price
                else:
                    self.balance[base] -= pnl / avg_order_price
        else:  # increase position, update position price (mean price)
            self.position['avgEntryPrice'] = (self.position['currentQty'] * self.position['avgEntryPrice'] +
                                              quote_volume * avg_order_price) / (
                                                     self.position['currentQty'] + quote_volume)
        self.position['currentQty'] += quote_volume
        self.set_liquidation_price(avg_order_price, base)

        logging.debug("balance: %s" % str(self.balance))
        logging.debug("position_updated: %s" % str(self.position))

    def on_event(self, event: Event):
        if isinstance(event, Trade):
            self.set_mark_price(event.payload)
            if self.position['currentQty'] > 0:
                if self.position['liquidationPrice'] >= self.position['markPrice']:
                    self.execute_liquidation(event.payload)

            elif self.position['currentQty'] < 0:
                if self.position['liquidationPrice'] <= self.position['markPrice']:
                    self.execute_liquidation(event.payload)

        if isinstance(event, Funding):
            base, quote = event.payload['symbol'].split('/')
            self.balance[base] -= self.position['currentQty'] * event.payload['rate'] / event.payload['price']
            self.funding_rate = {"timestamp": event.payload['timestamp'], "rate": event.payload['rate']}
        super().on_event(event)

    def execute_liquidation(self, trade):
        self.open_orders = {}
        for asset in self.balance.keys():
            self.balance[asset] = 0
        self.position = {"currentQty": 0,
                         "homeNotional": 0,
                         "avgEntryPrice": 0,
                         "liquidationPrice": None,
                         "openOrderBuyQty": None,
                         "openOrderSellQty": None,
                         "lastPrice": None,
                         "markPrice": None
                         }
        logging.warning("ALERT Liquidation executed %s" % str(self.position))
        self.dispatch(Liquidation(trade))
        raise InsufficientFunds("Zero balance: %s" % str(self.balance))

    def plot_balances(self, base, quote, price):
        exchange_date = datetime.fromtimestamp(self.timestamp / 1000.0).isoformat()
        value = self.balance[quote] + self.balance[base]
        quote_value = value * price
        self.dispatch(Plot({
            'name': 'Equity',
            'type': 'scatter',
            'mode': 'lines',
            'color': 'blue',
            'yaxis': 'balance',
            'data': {
                'x': exchange_date,
                'y': quote_value,
                'base_value': value,
                'position_vol': self.position['currentQty'],
                'position_price': self.position['avgEntryPrice'],
                'tooltip': "%.2f %s" % (quote_value, quote)
            },
        }))

    def funds_enough(self, order):
        sum_same_side_orders = sum([o['amount'] for o in self.open_orders.values() if o['side'] == order['side']])
        base, quote = order['symbol'].split('/')
        price = self.orderbooks[order['symbol']]['bids'][0][0]
        max_balance_avalable = self.balance[base] * price * self.leverage - abs(
            self.position["currentQty"]) - sum_same_side_orders
        return max_balance_avalable - order['amount'] >= 0

    def private_get_position(self):
        return [self.position]

    def set_mark_price(self, trade):
        """
        bitmex formula for markPrice/FairPrice
        FundingBasis = FundingRate * (Time Until Funding / Funding Interval)
        FairPrice = IndexPrice * (1 + Funding Basis)
        """
        if self.funding_rate is None:  # compatibility with no funding feeder
            self.position['markPrice'] = trade['price']
        else:
            time_until_founding = self.funding_rate['timestamp'] + 28800000 - trade['timestamp']
            founding_basis = self.funding_rate['rate'] * (time_until_founding / 28800000)
            self.position['markPrice'] = trade['price'] * (1 + founding_basis)

    def cancel_order(self, order_id, symbol=None, params={}):
        if order_id in self.open_orders:
            symbol = self.open_orders[order_id]['symbol']
            base = symbol.split('/')[0]
            mark_price = self.fetch_ticker(symbol)['bid']
            super().cancel_order(order_id, symbol, params)
            self.set_liquidation_price(mark_price, base)
        else:
            super().cancel_order(order_id, symbol, params)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        response = super().create_order(symbol, type, side, amount, price, params)
        base = symbol.split('/')[0]
        mark_price = self.fetch_ticker(symbol)['bid']
        self.set_liquidation_price(mark_price, base)
        return response

    def set_liquidation_price(self, mark_price, base):
        if abs(self.position['currentQty']) > 0:
            side = 'buy' if self.position['currentQty'] > 0 else 'sell'
            sum_same_side_orders = sum([o['amount'] for o in self.open_orders.values() if o['side'] == side])
            if self.position['currentQty'] < 0:
                sum_same_side_orders = -sum_same_side_orders

            price = list(self.orderbooks.values())[0]['bids'][0][0]
            max_cross_leverage = 100
            available_margin = self.balance[base] - abs(sum_same_side_orders / max_cross_leverage) / price

            bankruptcy_price = 1 / (1 / self.position['avgEntryPrice'] + available_margin / self.position['currentQty'])
            bankruptcy_value = self.position['currentQty'] * (1 / bankruptcy_price)
            funding_rate = self.funding_rate['rate'] if self.funding_rate else 0
            maintenance_margin = (0.005 * (self.position['currentQty'] / self.position['avgEntryPrice'])) + \
                                 (0.00075 * bankruptcy_value) + \
                                 (0.0001 * funding_rate)

            self.position['liquidationPrice'] = 1 / (
                        1 / self.position['avgEntryPrice'] + (available_margin - maintenance_margin) / self.position[
                    'currentQty'])
            if self.position['liquidationPrice'] < 0:
                self.position['liquidationPrice'] = 100000000.0  # bitmex max liquidation price
        else:
            self.position['liquidationPrice'] = None

    def fetch_balance(self):
        balances = {}
        symbol = list(self.orderbooks.keys())[0]
        price = list(self.orderbooks.values())[0]['bids'][0][0]
        base, quote = symbol.split('/')
        free_balance = self.fetch_free_balance()
        balances['free'] = free_balance
        used_balance = self.fetch_used_balance()
        balances['total'] = self.balance.copy()
        for asset in used_balance.keys():
            if asset == base:
                total = self.balance[asset]
                balances[asset] = {'free': free_balance[asset], 'used': used_balance[asset], 'total': total}
                balances['total'][asset] = total
                balances['info'] = [{'walletBalance': self.balance[asset] * 1e8}]
            else:
                balances[asset] = {'free': free_balance[asset], 'used': used_balance[asset],
                                   'total': self.balance[asset]}
        balances['used'] = used_balance
        return balances

    def fetch_free_balance(self):
        free_balance = self.balance.copy()
        base, quote = list(self.orderbooks.keys())[0].split('/')
        if len(self.open_orders) > 0:
            side = 'buy' if self.position['currentQty'] > 0 else 'sell'
            sum_same_side_orders = sum(
                [(o['amount'] / o['price']) for o in self.open_orders.values() if o['side'] == side])
            free_balance[base] -= sum_same_side_orders
        price = list(self.orderbooks.values())[0]['bids'][0][0]
        if abs(self.position['currentQty']) > 0:
            pnl = (price / self.position['avgEntryPrice'] * self.position['currentQty'] -
                   self.position['currentQty']) / price
            free_balance[base] += pnl
        return free_balance
