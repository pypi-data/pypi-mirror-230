from configcronos.core.entities import Phase1
from configcronos.core.repositories import Phase1Repository


class Phase1Service:

    def __init__(self, phase1_repository: Phase1Repository) -> None:
        self.phase1_repository = phase1_repository

    def get_phase1(self) -> Phase1:
        response = self.phase1_repository.get_phase1()
        data = response['data'][0]
        phase1 = Phase1(data['smarket_payload_max_length'], data['categories'], data['competitors'], data['coupons'], data['families'],
                            data['products'], data['products_associate'], data['research_products'], data['researches'], data['segments'],
                            data['stores'], data['stores_products'], data['suppliers'], data['gera_arquivo_envio'], data['lojas_ignoradas'],
                            data['divisoes_ignoradas'], data['segmentos_ignorados'], data['parametros_imposto'], data['parametros_custo_liquido'], data['converte_percentual_proporcao'],
                            data['data_inicio_cupons'], data['data_fim_cupons'], data['tipo_categoria'], data['quantidade_digitos_ean'], data['carrega_aliquotas'],
                            data['dias_semana_carga'], data['envia_notificacoes'], data['envia_dados_api'], data['endpoint_api_envio'], data['endpoint_api_envio_authentication'],
                            data['fragmento_produto_loja'])
        return phase1
    