from configcronos.core.entities import Schedule
from configcronos.core.repositories import ScheduleRepository


class ScheduleService:

    def __init__(self, schedule_repository: ScheduleRepository):
        self.schedule_repository = schedule_repository

    def get_schedule(self):

        response = self.schedule_repository.get_schedules()

        schedules = []

        for data in response['data']:
            schedules.append(Schedule(data['schedule_id'], data['command'], data['date_to_execute'], data['status'], data['modo_integracao']))

        return schedules

    def update_schedule(self, schedule):

        self.schedule_repository.update_schedule(schedule)

        return True
