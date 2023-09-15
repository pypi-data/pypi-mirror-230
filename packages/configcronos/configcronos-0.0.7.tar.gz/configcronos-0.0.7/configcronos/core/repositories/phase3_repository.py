from abc import ABC, abstractmethod


class Phase3Repository(ABC):

    @abstractmethod
    def __init__(self, headers):
        self.headers = headers

    @abstractmethod
    def get_phase3(self):
        pass
