from configcronos.core.repositories import PingerRepository
from configcronos.infra.configs import get_configs
from configcronos.core.errors import NoConection, NoDataFound
import requests
import json

env = get_configs()


class PingerRepositoryAPI(PingerRepository):

    def __init__(self, headers):
        self.headers = headers

    def ping(self, **kwargs):

        try:

            url = f"{env.API_CONFIGS_URL}/keepalive"
            body = {
                "message": str(kwargs.get("message")),
                "alive": bool(kwargs.get("alive")),
                "code": int(kwargs.get("code")),
                "modo_integracao": str(kwargs.get("modo_integracao")),
                "id_execucao": int(kwargs.get("id_execucao"))
            }

            response = requests.post(url=url, headers=self.headers, json=body)

            if response.status_code != 200:
                raise NoDataFound

            return response.json()

        except Exception:
            raise NoConection
