from configcronos.core.repositories import ScheduleRepository
import requests
from configcronos.infra.configs import get_configs
from configcronos.core.errors import NoConection, NoDataFound

env = get_configs()


class ScheduleRepositoryAPI(ScheduleRepository):

    def __init__(self, headers):
        self.headers = headers

    def get_schedules(self):
        url = f"{env.API_CONFIGS_URL}/schedule"
        try:
            response = requests.get(url=url, headers=self.headers)
            if response.status_code != 200:
                raise NoDataFound
            return response.json()
        except Exception:
            raise NoConection

    def update_schedule(self, schedule):
        url = f"{env.API_CONFIGS_URL}/schedule"
        try:
            response = requests.put(url=url, headers=self.headers, json=schedule.to_json())
            if response.status_code != 200:
                raise NoDataFound
            return response.json()
        except Exception:
            raise NoConection