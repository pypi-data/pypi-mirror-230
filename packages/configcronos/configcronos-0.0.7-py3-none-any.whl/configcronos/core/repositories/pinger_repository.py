from abc import ABC, abstractmethod


class PingerRepository(ABC):

    @abstractmethod
    def ping(self, **kwargs):
        pass
