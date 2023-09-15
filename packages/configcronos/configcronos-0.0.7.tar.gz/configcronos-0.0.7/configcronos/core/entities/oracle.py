class Oracle:

    def __init__(self, oracle_id: int, db_oracle_mode: str, db_sid: str, oracle_lib_dir: str):
        self.oracle_id = oracle_id
        self.db_oracle_mode = db_oracle_mode
        self.db_sid = db_sid
        self.oracle_lib_dir = oracle_lib_dir
