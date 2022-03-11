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
        self.balance_history = None
        self.last_balance_check = None

        self.peak_equity = 0
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
        if isinstance(event, Candle):
            self.update_balance_hist_from_candle(event)
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
                self.update_balance_hist_from_plot(event)

    def get_statistics(self):
        mdd = self.get_max_draw_down()
        return {'mdd': mdd}

    def update_balance_hist_from_plot(self, event):
        if self.last_price is not None:
            data = event.payload
            if self.balance_history is None:
                self.balance_history = [{'date': datetime.fromisoformat(data['data']['x'][0:10])}]

            if data['has_position']:
                self.balance_history[-1]['quote_balance'] = data['data']['quote_balance']
                self.balance_history[-1]['base_balance'] = data['data']['base_balance']
                self.balance_history[-1]['price'] = self.last_price
                self.balance_history[-1]['position_vol'] = data['data']['position_vol']
                self.balance_history[-1]['position_price'] = data['data']['position_price']
            else:
                self.balance_history[-1]['quote_balance'] = data['data']['quote_balance']
                self.balance_history[-1]['base_balance'] = data['data']['base_balance']
                self.balance_history[-1]['price'] = self.last_price

    def update_balance_hist_from_candle(self, event):
        data = event.payload
        date = datetime.fromisoformat(data['datetime'])
        if self.balance_history is not None and date - self.balance_history[-1]['date'] >= timedelta(days=1):
            # set prev balance close price and equity
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
                pnl = current_balance['position_vol'] * (current_balance['price'] - current_balance['position_price'])
                current_balance['equity'] += pnl / current_balance['price']
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
            profit = (self.balance_history[i+1][0] / self.balance_history[0][0] - 1) * 100
            profits_history.append(profit)

        standard_deviation = numpy.std(profits_history)
        time_delta_years = (self.balance_history[-1][1] - self.balance_history[0][1]).days / 365
        total_profit = (self.balance_history[-1][0] / self.balance_history[0][0] -1) * 100
        anual_profit = total_profit / time_delta_years
        no_risk_profit = 5
        sharpe_ratio = (anual_profit - no_risk_profit) / standard_deviation
        return sharpe_ratio