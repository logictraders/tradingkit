from abc import abstractmethod


class Fetcher:
    @abstractmethod
    def fetch(self, symbol, since8601, to8601=None):
        pass
