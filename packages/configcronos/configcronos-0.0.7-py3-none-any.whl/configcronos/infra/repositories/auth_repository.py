import datetime
import json
import time

import requests

from configcronos.infra.configs import get_configs

env = get_configs()


class AuthRepositoryAPI:
    def __init__(self):
        self.url = f"{env.API_CONFIGS_URL_AUTH}"

    def get_token(self) -> tuple[[str], [datetime]]:
        payload = {"username": env.USERNAME, "password": env.PASSWORD, "client_id": env.CLIENT_ID}
        response = requests.post(self.url, json=payload).json()
        epoch_exp = time.gmtime(response['exp'])
        year = epoch_exp.tm_year
        month = epoch_exp.tm_mon
        day = epoch_exp.tm_mday
        hour = epoch_exp.tm_hour
        minute = epoch_exp.tm_min
        second = epoch_exp.tm_sec

        date_exp = datetime.datetime(year, month, day, hour, minute, second)

        return response['access_token'], date_exp

if __name__ == "__main__":
    auth = AuthRepositoryAPI()
    print(auth.get_token())