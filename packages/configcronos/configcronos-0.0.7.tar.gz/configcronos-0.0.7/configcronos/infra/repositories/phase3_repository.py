from configcronos.core.repositories import Phase3Repository
from configcronos.core.errors import NoDataFound, NoConection
import requests
from configcronos.infra.configs import get_configs

env = get_configs()


class Phase3RepositoryAPI(Phase3Repository):

    def __init__(self, headers):
        self.headers = headers

    def get_phase3(self):
        url = f"{env.API_CONFIGS_URL}/phase3"

        try:
            response = requests.get(url=url, headers=self.headers)
            if response.status_code != 200:
                raise NoDataFound
            return response.json()
        except Exception:
            raise NoConection
