from __future__ import annotations

import re
from abc import abstractmethod

from tradingkit.pubsub.core.event import Event
from tradingkit.utils.serializable import Serializable


class State(Serializable):
    """
    We define a state object which provides some utility functions for the
    individual states within the state machine.
    """

    @abstractmethod
    def on_event(self, event: Event) -> State:
        """
        Handle events that are delegated to this State.
        """
        pass

    def on_create(self):
        """
        Executes in the constructor.
        """
        pass

    def __repr__(self):
        """
        Leverages the __str__ method to describe the State.
        """
        return self.__str__()

    def __str__(self):
        """
        Returns the name of the State.
        """
        state_filter = lambda attr: not re.match('^__.+__$', attr) and not callable(getattr(self, attr))
        attrs = {attr: getattr(self, attr) for attr in dir(self) if state_filter(attr)}
        return "%s(%s)" % (self.__class__.__name__, attrs)

    def serialize(self) -> str:
        return str(self)

    @staticmethod
    def unserialize(data: str):
        pass