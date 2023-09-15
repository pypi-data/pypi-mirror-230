from configcronos.core.entities import Database, Oracle
from configcronos.core.repositories import DatabaseRepository


class DatabaseService:

    def __init__(self, database_repository: DatabaseRepository) -> None:
        self.database_repository = database_repository

    def get_database(self, params: dict = None) -> Database:
        
        response = self.database_repository.get_database_by_params(params)
        data = response['data'][0]
        database = Database(data['database_id'], data['db_sgbd'], data['db_host'], 
                            data['db_username'], data['db_password'], data['db_port'], 
                            data['tipo_integracao'])
        return database

    def get_oracle(self, database_id: int) -> Oracle:

        response = self.database_repository.get_oracle_by_database_id(database_id)
        data = response['data'][0]
        oracle = Oracle(data['oracle_id'], data['db_oracle_mode'], data['db_sid'], data['oracle_lib_dir'])
        return oracle
