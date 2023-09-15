from configcronos.core.repositories import DatabaseRepository
from configcronos.core.errors import NoConection, NoDataFound
import requests
from configcronos.infra.configs import get_configs

env = get_configs()


class DatabaseRepositoryAPI(DatabaseRepository):

    def __init__(self, headers):
        self.headers = headers

    def get_database_by_id(self, database_id):
        pass

    def get_database_by_params(self, raw_params=None) -> dict[list]:
        # headers = {"x-smarket-user": 'teste', 'x-smarket-client-id': "barcelos", "x-smarket-user-id": "teste"}
        url = f"{env.API_CONFIGS_URL}/clients/databases?"
        if raw_params:
            params = '' 
            for key, value in raw_params.items():
                params += f'{key}={value}&'
            url += params

        try:
            response = requests.get(url=url, headers=self.headers)
            if response.status_code != 200:
                raise NoDataFound
            return response.json()
        except Exception:
            raise NoConection

    def get_oracle_by_database_id(self, database_id):
        url = f"{env.API_CONFIGS_URL}/clients/databases/{database_id}/oracle"
        try:
            response = requests.get(url=url, headers=self.headers)
            if response.status_code != 200:
                raise NoDataFound
            return response.json()
        except Exception:
            raise NoConection