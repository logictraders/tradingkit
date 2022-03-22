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

        self.balance_history = None
        self.last_balance_check = None

        self.peak_equity = 0
        self.max_drawdown = 0
        self.last_price = None
        self.last_trade_timestamp = None
        self.max_no_trades_time = 0
        self.volume_traded = 0

    def subscribed_events(self) -> list:
        return [Order, Trade, Book, Candle, Liquidation, Funding, OpenOrder, Plot]

    def on_event(self, event: Event):
        if isinstance(event, Book):
            self.last_price = event.payload['bids'][0][0]

        if isinstance(event, Candle):
            if event.payload['timeframe'] == '1d':
                self.update_balance_hist_from_candle(event)

        if isinstance(event, Trade):
            self.last_price = event.payload['price']

        if isinstance(event, Plot):
            if event.payload['name'] == 'Equity':
                self.update_balance_hist_from_plot(event)

        if isinstance(event, Order):
            order = event.payload.copy()
            amount = order['amount'] / order['price'] if order['exchange'] == 'bitmex' else order['amount'] * order['price']
            self.update_trades_statistics(order['lastTradeTimestamp'], amount)

    def get_statistics(self):
        max_drawdown = self.get_max_draw_down()
        sharpe_ratio = self.get_sharpe_ratio()
        self.update_trades_statistics(self.balance_history[-1]['date'].timestamp() * 1000, 0)
        return {'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'days_running': (self.balance_history[-1]['date'] - self.balance_history[0]['date']).days,
                'max_no_trading_days': self.max_no_trades_time / 1000 / 60 / 60 / 24,
                'volume_traded': self.volume_traded,
                }

    def update_balance_hist_from_plot(self, event):
        data = event.payload
        if self.balance_history is None:
            date = datetime.fromisoformat(data['data']['x'][0:10])
            self.balance_history = [{'date': date, 'price': data['price']}]
            self.last_trade_timestamp = date.timestamp() * 1000

        if data['has_position']:
            self.balance_history[-1]['quote_balance'] = data['data']['quote_balance']
            self.balance_history[-1]['base_balance'] = data['data']['base_balance']
            self.balance_history[-1]['position_vol'] = data['data']['position_vol']
            self.balance_history[-1]['position_price'] = data['data']['position_price']
        else:
            self.balance_history[-1]['quote_balance'] = data['data']['quote_balance']
            self.balance_history[-1]['base_balance'] = data['data']['base_balance']

    def update_balance_hist_from_candle(self, event):
        data = event.payload
        date = datetime.fromisoformat(data['datetime'])
        if self.balance_history is not None and date - self.balance_history[-1]['date'] >= timedelta(days=1):
            self.balance_history[-1]['price'] = self.last_price
            self.balance_history[-1] = self.calculate_equity(self.balance_history[-1])

            # set current balance
            current_balance = self.balance_history[-1].copy()
            current_balance['date'] = datetime.fromisoformat(data['datetime'][0:10])
            self.balance_history.append(current_balance)

            self.calculate_max_drawdown()

    def calculate_equity(self, current_balance):
        if 'position_vol' in current_balance.keys():
            current_balance['equity'] = current_balance['base_balance'] + current_balance['quote_balance'] / \
                                        current_balance['price']
            if current_balance['position_vol'] != 0:
                pnl = (1 / current_balance['position_price'] - 1 / current_balance['price']) * current_balance['position_vol']
                current_balance['equity'] += pnl
        else:
            current_balance['equity'] = current_balance['quote_balance'] + current_balance['base_balance'] * \
                                        current_balance['price']
        return current_balance

    def calculate_max_drawdown(self):
        equity = self.balance_history[-1]['equity']

        if equity > self.peak_equity:
            self.peak_equity = equity

        drawdown = (equity - self.peak_equity) / self.peak_equity
        self.max_drawdown = min(self.max_drawdown, drawdown)

    def get_max_draw_down(self):
        # set last balance price and equity
        self.balance_history[-1]['price'] = self.last_price
        self.balance_history[-1] = self.calculate_equity(self.balance_history[-1])

        self.calculate_max_drawdown()
        return self.max_drawdown

    def get_sharpe_ratio(self):
        profits_history = []
        for i in range(len(self.balance_history) - 1):
            profit = (self.balance_history[i + 1]['equity'] / self.balance_history[0]['equity'] - 1) * 100
            profits_history.append(profit)

        standard_deviation = numpy.std(profits_history)
        time_delta_years = (self.balance_history[-1]['date'] - self.balance_history[0]['date']).days / 365
        total_profit = (self.balance_history[-1]['equity'] / self.balance_history[0]['equity'] - 1) * 100
        if time_delta_years == 0:
            return 0
        anual_profit = total_profit / time_delta_years
        no_risk_profit = 5
        sharpe_ratio = (anual_profit - no_risk_profit) / standard_deviation
        return sharpe_ratio

    def update_trades_statistics(self, timestamp, amount):
        if self.last_trade_timestamp is None:
            self.last_trade_timestamp = timestamp
        else:
            self.max_no_trades_time = max(self.max_no_trades_time, timestamp - self.last_trade_timestamp)
            self.last_trade_timestamp = timestamp

        self.volume_traded += amount