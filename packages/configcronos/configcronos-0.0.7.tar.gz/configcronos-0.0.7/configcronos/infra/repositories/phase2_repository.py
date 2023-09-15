from configcronos.core.repositories import Phase2Repository
from configcronos.core.errors import NoDataFound, NoConection
import requests 
from configcronos.infra.configs import get_configs

env = get_configs()


class Phase2RepositoryAPI(Phase2Repository):

    def __init__(self, headers):
        self.headers = headers

    def get_phase2(self):
        #headers = {"x-smarket-user": 'teste', 'x-smarket-client-id': "barcelos", "x-smarket-user-id": "teste"}
        url = f"{env.API_CONFIGS_URL}/phase2"
        try:
            response = requests.get(url=url, headers=self.headers)
            if response.status_code != 200:
                raise NoDataFound
            return response.json()
        except Exception:
            raise NoConection
