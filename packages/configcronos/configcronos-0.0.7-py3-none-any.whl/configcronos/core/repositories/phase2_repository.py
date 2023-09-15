from abc import ABC, abstractmethod


class Phase2Repository(ABC):

    @abstractmethod
    def __init__(self, headers):
        self.headers = headers

    @abstractmethod
    def get_phase2(self):
        pass
