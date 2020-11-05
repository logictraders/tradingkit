from tradingkit.pubsub.core.event import Event
from tradingkit.strategy.strategy import Strategy


class StrategyEvent(Event):
    def __init__(self, payload, strategy: Strategy):
        super().__init__(payload)
        self.strategy = strategy
