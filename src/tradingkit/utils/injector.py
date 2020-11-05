from abc import abstractmethod


class Injector:

    @abstractmethod
    def inject(self, config, kind):
        pass
