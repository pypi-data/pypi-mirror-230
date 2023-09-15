from abc import ABC, abstractmethod


class SegmentRepository(ABC):

    @abstractmethod
    def get_segments(self):
        pass
