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
        self.balance_history = []
        self.last_balance_check = None
        self.peak_balance = 0
        self.max_drawdown = 0
        self.last_price = None
        self.symbol = None

    def subscribed_events(self) -> list:
        return [Order, Trade, Book, Candle, Liquidation, Funding, OpenOrder, Plot]

    def on_event(self, event: Event):
        self.dispatch(event)

    def get_statistics(self):
        return {'MDD': -0.2}

    def update_balance_hist(self, event):
        date = datetime.fromisoformat(event.payload['datetime'])
        if self.last_balance_check is None or date - self.last_balance_check >= timedelta(days=1):
            self.last_balance_check = date

            price = event.payload['close']
            base, quote = self.symbol.split('/')
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