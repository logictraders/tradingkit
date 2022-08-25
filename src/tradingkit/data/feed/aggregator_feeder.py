import time
import multiprocessing

from tradingkit.data.feed.feeder import Feeder
from tradingkit.pubsub.core.event import Event
from tradingkit.pubsub.core.publisher import Publisher
from tradingkit.pubsub.core.subscriber import Subscriber
from tradingkit.pubsub.event.book import Book
from tradingkit.pubsub.event.candle import Candle
from tradingkit.pubsub.event.order import Order
from tradingkit.pubsub.event.position import Position
from tradingkit.pubsub.event.trade import Trade


class AggregatorFeeder(Feeder, Subscriber, Publisher):

    def __init__(self, feeders):
        super().__init__()
        self.feeders = feeders

    def subscribed_events(self) -> list:
        return [Order, Book, Trade, Candle, Position]

    def on_event(self, event: Event):
        self.dispatch(event)

    def feed(self):
        children = []
        for feeder in self.feeders:
            feeder.register(self)
            child = multiprocessing.Process(target=feeder.feed)
            child.daemon = True
            child.start()
            children.append(child)

        # Active loop to check feeder children
        while True:
            time.sleep(1)
            for child in children:
                if not child.is_alive():
                    raise ValueError("Feeder process %d ended" % child.pid)
