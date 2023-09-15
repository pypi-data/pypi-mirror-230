from configcronos.core.repositories import SegmentRepository
from configcronos.infra.configs import get_configs
from configcronos.core.errors import NoConection, NoDataFound
import requests

env = get_configs()


class SegmentRepositoryAPI(SegmentRepository):

    def __init__(self, headers):
        self.headers = headers

    def get_segments(self):

        try:
            url = f"{env.API_CONFIGS_URL}/segments"
            response = requests.get(url=url, headers=self.headers)

            if response.status_code != 200:
                raise NoDataFound

            return response.json()

        except Exception:
            raise NoConection
