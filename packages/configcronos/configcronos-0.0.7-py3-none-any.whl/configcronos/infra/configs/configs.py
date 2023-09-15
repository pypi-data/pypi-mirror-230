import dotenv
from functools import lru_cache
import os


class Configs:

    def __init__(self):

        dotenv.load_dotenv(override=True)
        self.API_CONFIGS_URL = os.getenv("API_CONFIGS_URL", "https://api-gateway.smarketsolutions.com.br/v1/atenas")
        self.USERNAME = os.getenv("USERNAME_SMARKET", "davi_araujo")
        self.PASSWORD = os.getenv("PASSWORD_SMARKET", "Smarket@2022")
        self.CLIENT_ID = os.getenv("CLIENT_ID_SMARKET", "onboarding")
        self.API_CONFIGS_URL_AUTH = os.getenv("API_CONFIGS_URL_AUTH", "https://api-gateway.smarketsolutions.com.br/auth/token")

@lru_cache()
def get_configs():
    """Helper function to get env with lru cache"""
    return Configs()
