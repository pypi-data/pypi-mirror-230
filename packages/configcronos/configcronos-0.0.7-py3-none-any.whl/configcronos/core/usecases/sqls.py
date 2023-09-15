from configcronos.core.entities import SQLs
from configcronos.core.repositories import SQLsRepository

class SQLsService:

    def __init__(self, sqls_repository: SQLsRepository) -> None:
        self.sqls_repository = sqls_repository

    def get_sqls(self) -> SQLs:

        response = self.sqls_repository.get_sqls()
        data = response['data'][0]
        sqls = SQLs(data['sqls_envio'], data['sqls_retorno'])
        return sqls
