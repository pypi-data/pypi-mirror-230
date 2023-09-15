class NoDataFound(Exception):

    def __init__(self):
        self.message = 'Não foi possível encontrar dados para o cliente solicitado'
        super().__init__(self.message)
