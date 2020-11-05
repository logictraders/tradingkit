from abc import abstractmethod


class Serializable:
    @abstractmethod
    def serialize(self) -> str:
        pass

    @staticmethod
    @abstractmethod
    def unserialize(data: str):
        pass