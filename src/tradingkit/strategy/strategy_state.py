from __future__ import annotations

import json
from abc import abstractmethod

from tradingkit.state_machine.state import State
from tradingkit.strategy.strategy_event import StrategyEvent


class StrategyState(State):

    @abstractmethod
    def on_event(self, strategy_event: StrategyEvent) -> StrategyState:
        pass

    def serialize(self) -> str:
        return json.dumps(self)

    @staticmethod
    def unserialize(data: str):
        return json.loads(data)
