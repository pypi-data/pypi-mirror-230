from configcronos.core.repositories import SQLsRepository
from configcronos.core.errors import NoConection, NoDataFound
import requests
from configcronos.infra.configs import get_configs

env = get_configs()


class SQLsRepositoryAPI(SQLsRepository):

        def __init__(self, headers):
            self.headers = headers

        def get_sqls(self):
            url = f"{env.API_CONFIGS_URL}/sqls"
            try:
                response = requests.get(url=url, headers=self.headers)
                if response.status_code != 200:
                    raise NoDataFound
                return response.json()
            except Exception:
                raise NoConection