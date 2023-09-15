from configcronos.core.repositories import ClientRepository
from configcronos.infra.configs import get_configs
from configcronos.core.errors import NoConection, NoDataFound
import requests

env = get_configs()


class ClientRepositoryAPI(ClientRepository):

    def __init__(self, headers):
        self.headers = headers

    def get_client(self):

        try:
            #headers = {"x-smarket-user": 'teste', 'x-smarket-client-id': "barcelos", "x-smarket-user-id": "teste"}
            url = f"{env.API_CONFIGS_URL}/clients"
            response = requests.get(url, headers=self.headers)

            if response.status_code != 200:
                raise NoDataFound

            return response.json()

        except Exception:

            raise NoConection

    def put_client_version(self):
        pass

