from datetime import datetime, timedelta

import numpy

from tradingkit.pubsub.core.event import Event
from tradingkit.pubsub.core.publisher import Publisher
from tradingkit.pubsub.core.subscriber import Subscriber
from tradingkit.pubsub.event.book import Book
from tradingkit.pubsub.event.candle import Candle
from tradingkit.pubsub.event.funding import Funding
from tradingkit.pubsub.event.liquidation import Liquidation
from tradingkit.pubsub.event.open_order import OpenOrder
from tradingkit.pubsub.event.order import Order
from tradingkit.pubsub.event.plot import Plot
from tradingkit.pubsub.event.trade import Trade


class Statistics(Publisher, Subscriber):

    def __init__(self):
        super().__init__()

        self.exchange_name = None
        self.balance_history = []
        self.last_balance_check = None

        self.peak_balance = 0
        self.max_drawdown = 0
        self.last_price = None
        self.symbol = None

    def subscribed_events(self) -> list:
        return [Order, Trade, Book, Candle, Liquidation, Funding, OpenOrder, Plot]

    def on_event(self, event: Event):
        if isinstance(event, Book):
            self.last_price = event.payload['bids'][0][0]
        #     if self.last_price is None:
        #         self.calculate_exchange_state(event.payload['timestamp'], event.payload['symbol'], event.payload['bids'][0][0])
        #         self.symbol = event.payload['symbol']
        # if isinstance(event, Candle):
        #     self.plot_candle(event)
        #     if self.is_backtest:
        #         self.update_balance_hist(event)
        # if isinstance(event, Order):
        #     order = event.payload.copy()
        #     if order['id'] in self.orders_history.keys():
        #         self.orders_history[order['id']].update(order)
        #         event.payload = self.orders_history[order['id']]
        #     self.plot_order(event)
        #     self.calculate_exchange_state(order['lastTradeTimestamp'], order['symbol'], self.last_price)
        # if isinstance(event, OpenOrder):
        #     self.plot_order(event)
        #     order = event.payload.copy()
        #     self.calculate_exchange_state(order['timestamp'], order['symbol'], self.last_price)
        # if isinstance(event, Liquidation):
        #     trade = event.payload
        #     self.calculate_exchange_state(trade['timestamp'], trade['symbol'], trade['price'])
        if isinstance(event, Trade):
            trade = event.payload
            self.last_price = event.payload['price']
        #     if self.symbol is None:
        #         self.symbol = event.payload['symbol']
        #     self.candle_dispatcher(trade)
        if isinstance(event, Plot):
            if event.payload['name'] == 'Equity':
                self.update_balance_hist(event)

    def get_statistics(self):
        return {'MDD': -0.2}

    def update_balance_hist(self, event):
        date = datetime.fromisoformat(event.payload['data']['x'])
        if self.last_balance_check is None or date - self.last_balance_check >= timedelta(days=1):
            self.last_balance_check = date

            price = self.last_price
            base = event.payload['base']
            quote = event.payload['quote']
            _balances = self.fetch_balance()

            if self.has_position:
                balances = _balances['free']
                base_balance = balances[base] if base in balances else 0
                quote_balance = balances[quote] if quote in balances else 0
                base_equity = base_balance + quote_balance / price
                self.balance_history.append([base_equity, date])
            else:
                balances = _balances['total']
                base_balance = balances[base] if base in balances else 0
                quote_balance = balances[quote] if quote in balances else 0
                quote_equity = quote_balance + base_balance * price
                self.balance_history.append([quote_equity, date])

            self.calculate_max_drawdown(_balances['total'][base], _balances['total'][quote])

    def calculate_max_drawdown(self, base_balance, quote_balance):
        if self.last_price:
            balance = quote_balance + base_balance * self.last_price if not self.has_position else base_balance

            if self.has_position:
                position = self.private_get_position()[0]
                if abs(position['currentQty']) > 0:
                    pnl = (self.last_price / position['avgEntryPrice'] * position['currentQty'] -
                           position['currentQty']) / self.last_price
                    balance += pnl / self.last_price

            if balance > self.peak_balance:
                self.peak_balance = balance

            drawdown = (balance - self.peak_balance) / self.peak_balance
            self.max_drawdown = min(self.max_drawdown, drawdown)

    def get_sharpe_ratio(self):
        profits_history = []
        for i in range(len(self.balance_history) - 1):
            profit = (self.balance_history[i+1][0] / self.balance_history[0][0] - 1) * 100
            profits_history.append(profit)

        standard_deviation = numpy.std(profits_history)
        time_delta_years = (self.balance_history[-1][1] - self.balance_history[0][1]).days / 365
        total_profit = (self.balance_history[-1][0] / self.balance_history[0][0] -1) * 100
        anual_profit = total_profit / time_delta_years
        no_risk_profit = 5
        sharpe_ratio = (anual_profit - no_risk_profit) / standard_deviation
        return sharpe_ratio