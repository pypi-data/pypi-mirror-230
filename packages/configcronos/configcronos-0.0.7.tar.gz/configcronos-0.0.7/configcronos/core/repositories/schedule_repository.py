from abc import ABC, abstractmethod


class ScheduleRepository(ABC):

    def __init__(self, headers):
        pass

    @abstractmethod
    def get_schedules(self):
        pass

    @abstractmethod
    def update_schedule(self, schedule):
        pass
