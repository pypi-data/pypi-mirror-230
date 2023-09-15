class Pinger:

    def __init__(self, message: str = 'PING', alive: bool = True, code: int = 99):
        self.message = message
        self.alive = alive
        self.code = code
