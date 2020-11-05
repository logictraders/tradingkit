from tradingkit.display.plotter import Plotter
from tradingkit.pubsub.core.event import Event


class NonePlotter(Plotter):
    """ This Plotter does nothing """

    def on_event(self, event: Event):
        pass
