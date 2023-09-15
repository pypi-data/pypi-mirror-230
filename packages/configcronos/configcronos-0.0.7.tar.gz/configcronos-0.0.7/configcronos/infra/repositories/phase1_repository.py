from configcronos.core.repositories import Phase1Repository
from configcronos.core.errors import NoConection, NoDataFound
import requests 
from configcronos.infra.configs import get_configs

env = get_configs()


class Phase1RepositoryAPI(Phase1Repository):

    def get_phase1(self):
        headers = {"x-smarket-user": 'teste', 'x-smarket-client-id': "barcelos", "x-smarket-user-id": "teste"}
        url = f"{env.API_CONFIGS_URL}/phase1"
        try:
            response = requests.get(url=url, headers=headers)
            if response.status_code != 200:
                raise NoDataFound
            return response.json()
        except Exception:
            raise NoConection
