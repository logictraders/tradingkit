import logging
from abc import abstractmethod

from ccxt import Exchange

from tradingkit.pubsub.core.event import Event
from tradingkit.strategy.strategy import Strategy
from tradingkit.strategy.strategy_event import StrategyEvent


class StateMachineStrategy(Strategy):

    def __init__(self, exchange: Exchange, config=None):
        super().__init__(exchange, config)
        self.state = None
        self.prev = None

    def start(self):
        super().start()
        self.state = self.recover_state() or self.initial_state()

    def on_event(self, event: Event):
        super().on_event(event)
        if self.prev != self.state:
            logging.info("StateMachineStrategy.on_event(%s), state: %s" % (str(event.__class__), self.state))
            logging.info("State change: %s -> %s" % (self.prev, self.state))
            self.prev = self.state
        logging.debug("Event: %s: %s" % (event.__class__.__name__, event.payload))
        self.state = self.state.on_event(StrategyEvent(event, self))

    def recover_state(self):
        return None

    @abstractmethod
    def initial_state(self):
        pass
