from tradingkit.data.adapter.adapter import Adapter
from tradingkit.pubsub.core.event import Event
from tradingkit.pubsub.event.trade import Trade


class OutlierTradeFilter(Adapter):
    """
    Detects anomalies based on last trade price
    Takes the trade and checks if price changed more than the :max_rate permitted
    If anomaly is detected, it returns the last trade whithout bias.
    """

    def __init__(self, max_rate):
        super().__init__()
        self.max_rate = max_rate
        self.last_trade = None

    def adapt(self, event: Event) -> Event:
        trade = event.payload
        if self.last_trade is None:
            self.last_trade = trade
            return event

        change_rate = abs(trade['price'] - self.last_trade['price']) / self.last_trade['price']
        if change_rate > self.max_rate:
            corrected_trade = self.last_trade.copy()
            corrected_trade['timestamp'] = trade['timestamp']
            return Trade(corrected_trade)

        self.last_trade = trade
        return event

    def subscribed_events(self) -> list:
        return [Trade]
