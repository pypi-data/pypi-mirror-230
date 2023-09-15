from configcronos.core.entities import Client
from configcronos.core.repositories import ClientRepository


class ClientService:

    def __init__(self, client_repository: ClientRepository):
        self.client_repository = client_repository

    def get_client(self):

        response = self.client_repository.get_client()

        data = response['data'][0]

        client = Client(data['client_id'], data['client_name'], data['token_envio'], data['token_retorno'], data['versao_cronos'])

        return client

