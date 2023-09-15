class Client:

    def __init__(self, client_id, client_name, token_envio, token_retorno, versao_cronos):
        self.client_id = client_id
        self.client_name = client_name
        self.token_envio = token_envio
        self.token_retorno = token_retorno
        self.versao_cronos = versao_cronos

    def __repr__(self):
        return f'Client(client_id={self.client_id}, client_name={self.client_name}, token_envio={self.token_envio}, token_retorno={self.token_retorno}, versao_cronos={self.versao_cronos})'