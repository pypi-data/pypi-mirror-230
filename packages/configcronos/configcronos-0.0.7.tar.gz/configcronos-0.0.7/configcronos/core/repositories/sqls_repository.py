from abc import ABC, abstractmethod


class SQLsRepository(ABC):

    @abstractmethod
    def __init__(self, headers):
        pass

    @abstractmethod
    def get_sqls(self):
        pass