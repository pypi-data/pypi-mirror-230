class Database:

    def __init__(self, database_id: int, db_sgbd: str, db_host: str, db_username: str, db_password: str, db_port: str, tipo_integracao: str) -> None:
        self.database_id = database_id
        self.db_sgbd = db_sgbd
        self.db_host = db_host
        self.db_username = db_username
        self.db_password = db_password
        self.db_port = db_port
        self.tipo_integracao = tipo_integracao
        self.oracle = None
