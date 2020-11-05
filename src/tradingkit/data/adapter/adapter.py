from abc import abstractmethod

from tradingkit.pubsub.core.event import Event
from tradingkit.pubsub.core.publisher import Publisher
from tradingkit.pubsub.core.subscriber import Subscriber


class Adapter(Subscriber, Publisher):

    @abstractmethod
    def adapt(self, event: Event) -> Event:
        pass

    def on_event(self, event: Event):
        self.dispatch(self.adapt(event))
