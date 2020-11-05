from tradingkit.pubsub.core.event import Event
from tradingkit.pubsub.core.subscriber import Subscriber


class Publisher:

    def __init__(self):
        self.events = {}

    def register(self, subscriber: Subscriber):
        for event in subscriber.subscribed_events():
            if event not in self.events:
                self.events[event] = []
            self.events[event].append(subscriber)

    def unregister(self, subscriber: Subscriber):
        for event in subscriber.subscribed_events():
            self.events[event].remove(subscriber)

    def dispatch(self, event: Event):
        if event.__class__ in self.events:
            for subscriber in self.events[event.__class__]:
                subscriber.on_event(event)
