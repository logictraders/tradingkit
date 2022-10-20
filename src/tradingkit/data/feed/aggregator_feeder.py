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
        self.pr, self.pw = multiprocessing.Pipe()

    def subscribed_events(self) -> list:
        return [Order, Book, Trade, Candle, Position]

    def on_event(self, event: Event):
        parent = multiprocessing.parent_process()
        if parent is None:  # main process, dispatch event
            self.dispatch(event)
        else:  # child process, send by pipe to parent
            self.pw.send(event)

    def feed(self):
        children = []
        for feeder in self.feeders:
            feeder.register(self)
            child = multiprocessing.Process(target=feeder.feed)
            child.daemon = True
            child.start()
            children.append(child)

        event = self.pr.recv()
        while event:
            self.dispatch(event)
            event = self.pr.recv()
            if len(multiprocessing.active_children()) < len(self.feeders):
                raise ValueError("Feeder process ended, ending main process too")

        raise ValueError("All feeders ended")
