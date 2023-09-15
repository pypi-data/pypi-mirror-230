from abc import ABC, abstractmethod


class ClientRepository(ABC):

    @abstractmethod
    def __init__(self, headers):
        self.headers = headers

    @abstractmethod
    def get_client(self):
        pass

    def put_client_version(self):
        pass

