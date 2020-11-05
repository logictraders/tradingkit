from tradingkit.strategy.strategy import Strategy


class NoneStrategy(Strategy):

    def get_symbol(self):
        return 'BTC/USD'

    def subscribed_events(self) -> list:
        return []

    def finish(self):
        return {}
