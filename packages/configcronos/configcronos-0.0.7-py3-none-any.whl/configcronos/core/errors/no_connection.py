class NoConection(Exception):

    def __init__(self):
        self.message = "Não foi possível conectar a API de Configs Athenas"
        super().__init__(self.message)

