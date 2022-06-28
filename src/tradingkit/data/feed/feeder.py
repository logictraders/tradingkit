from abc import abstractmethod


class Feeder:
    @abstractmethod
    def feed(self):
        pass

    def set_name(self, name):
        self.name = name