from tradingkit.data.adapter.adapter import Adapter
from tradingkit.pubsub.core.event import Event
from tradingkit.pubsub.event.book import Book
from tradingkit.pubsub.event.candle import Candle
from tradingkit.pubsub.event.funding import Funding
from tradingkit.pubsub.event.liquidation import Liquidation
from tradingkit.pubsub.event.open_order import OpenOrder
from tradingkit.pubsub.event.order import Order
from tradingkit.pubsub.event.trade import Trade


class FeedersSycronizer(Adapter):

    def __init__(self, lock):
        super().__init__()
        self.lock = lock

    def on_event(self, event: Event):
        self.lock.acquire()
        self.dispatch(event)
        self.lock.release()

    def subscribed_events(self) -> list:
        return [Order, Trade, Book, Candle, Liquidation, Funding, OpenOrder]
