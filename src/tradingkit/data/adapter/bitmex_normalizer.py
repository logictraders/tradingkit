from tradingkit.data.adapter.adapter import Adapter
from tradingkit.pubsub.core.event import Event
from tradingkit.pubsub.event.trade import Trade


class BitmexNormalizer(Adapter):

    def __init__(self, symbol):
        super().__init__()
        self.symbol = symbol

    def adapt(self, event: Event) -> Event:
        trade = event.payload.copy()
        trade['symbol'] = self.symbol
        trade['cost'] = trade['amount']
        trade['amount'] = trade['amount'] / trade['price']
        return Trade(trade)

    def subscribed_events(self) -> list:
        return [Trade]
