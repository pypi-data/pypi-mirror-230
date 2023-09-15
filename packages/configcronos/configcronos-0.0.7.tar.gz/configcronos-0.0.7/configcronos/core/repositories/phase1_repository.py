from abc import ABC, abstractmethod


class Phase1Repository(ABC):

    @abstractmethod
    def __init__(self, headers):
        self.headers = headers

    @abstractmethod
    def get_phase1(self):
        pass
    