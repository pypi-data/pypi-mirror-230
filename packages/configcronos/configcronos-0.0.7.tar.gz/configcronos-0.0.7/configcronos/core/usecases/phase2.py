from configcronos.core.entities import Phase2
from configcronos.core.repositories import Phase2Repository


class Phase2Service:

    def __init__(self, phase2_repository: Phase2Repository) -> None:
        self.phase2_repository = phase2_repository

    def get_phase2(self) -> Phase2:
        response = self.phase2_repository.get_phase2()
        data = response['data'][0]
        phase2 = Phase2(data['client_id'],
                        data['db_config_id'],
                        data['integrador_parcial'],
                        data['forcar_campanha'],
                        data['modo'],
                        data['erp'],
                        data['log_info'],
                        data['modo_custo'],
                        data['update_remoto'],
                        data['gera_custo_verba'],
                        data['integra_familia'],
                        data['tipos_por_familia'],
                        data['integra_associados'],
                        data['tipos_por_associado'],
                        data['pack_valor_brinde'],
                        data['pague_leve_valor_brinde'],
                        data['desconto_unidade_proporcional'],
                        data['desconto_unidade_valor'],
                        data['integra_normal'],
                        data['integra_de_por'],
                        data['integra_pack_virtual'],
                        data['integra_pack_cooperado'],
                        data['integra_pague_leve'],
                        data['integra_pague_leve_cooperado'],
                        data['integra_atacado'],
                        data['integra_atacado_muffato'],
                        data['integra_desconto'],
                        data['integra_desconto_cooperado'],
                        data['integra_fidelidade'],
                        data['integra_fidelidade_muffato'],
                        data['integra_escalonada'],
                        data['integra_combo'],
                        data['integra_atacado_fidelidade'],
                        data['integra_pack_desconto'],
                        data['integra_cartao'],
                        data['integra_cashback'],
                        data['integra_cashback_porcentagem'],
                        data['consinco_gerenciador_precos'],
                        data['consinco_produtos_promocionais'],
                        data['consinco_regra_incentivo'],
                        data['consinco_monitor'])
        return phase2
    