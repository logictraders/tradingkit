from tradingkit.data.feed.feeder import Feeder
from tradingkit.pubsub.core.publisher import Publisher
from tradingkit.pubsub.event.trade import Trade


class ListFeeder(Feeder, Publisher):
    def __init__(self, trades):
        super().__init__()
        self.trades = trades
        self.name = 'list_feeder'

    def feed(self):
        for trade in self.trades:
            self.dispatch(Trade(trade))
