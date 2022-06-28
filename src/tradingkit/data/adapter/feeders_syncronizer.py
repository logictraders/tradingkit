from tradingkit.data.adapter.adapter import Adapter
from tradingkit.pubsub.core.event import Event
from tradingkit.pubsub.event.book import Book
from tradingkit.pubsub.event.candle import Candle
from tradingkit.pubsub.event.funding import Funding
from tradingkit.pubsub.event.liquidation import Liquidation
from tradingkit.pubsub.event.open_order import OpenOrder
from tradingkit.pubsub.event.order import Order
from tradingkit.pubsub.event.trade import Trade
import time, datetime, heapq



class FeedersSycronizer(Adapter):

    def __init__(self, lock):
        super().__init__()
        self.lock = lock
        self.feeders_events = {}

    def add_feeder(self, name):
        self.feeders_events[name] = []

    def on_event(self, event: Event):
        self.lock.acquire()
        if self.feeders_events == {}:  # live
            self.dispatch(event)
        else: # backtest
            self.feeders_events[event.payload['exchange']].append(event)
            feeders_events = self.feeders_events.values()
            if [] not in feeders_events: # all feeders have at least one event in list
                oldest_event = None
                for feeder_events in feeders_events:
                    if oldest_event is None or feeder_events[0].payload['timestamp'] < oldest_event.payload['timestamp']:
                        oldest_event = feeder_events[0]

                self.feeders_events[oldest_event.payload['exchange']].pop(0)
                self.dispatch(oldest_event)

        self.lock.release()

    def subscribed_events(self) -> list:
        return [Order, Trade, Book, Candle, Liquidation, Funding, OpenOrder]
