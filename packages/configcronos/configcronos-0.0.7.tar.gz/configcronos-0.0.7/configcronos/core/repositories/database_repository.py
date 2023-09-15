from abc import ABC, abstractmethod


class DatabaseRepository(ABC):

    @abstractmethod
    def __init__(self, headers):
        self.headers = headers

    @abstractmethod
    def get_database_by_params(self, params):
        pass

    @abstractmethod
    def get_database_by_id(self, database_id):
        pass

    @abstractmethod
    def get_oracle_by_database_id(self, database_id):
        pass


