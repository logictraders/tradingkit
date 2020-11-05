from abc import abstractmethod

from tradingkit.pubsub.core.event import Event


class Subscriber:

    @abstractmethod
    def subscribed_events(self) -> list:
        pass

    @abstractmethod
    def on_event(self, event: Event):
        pass
