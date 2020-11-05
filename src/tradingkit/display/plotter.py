from abc import ABC

from tradingkit.pubsub.core.subscriber import Subscriber
from tradingkit.pubsub.event.plot import Plot


class Plotter(Subscriber, ABC):

    def subscribed_events(self) -> list:
        return [Plot]
