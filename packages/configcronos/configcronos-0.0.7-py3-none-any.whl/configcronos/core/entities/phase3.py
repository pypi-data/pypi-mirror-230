class Phase3:

    def __init__(self,
                 client_id,
                 db_config_id,
                 forcar_campanha,
                 erp,
                 log_info,
                 integra_normal,
                 integra_de_por,
                 integra_pack_virtual,
                 integra_pack_cooperado,
                 integra_pague_leve,
                 integra_pague_leve_cooperado,
                 integra_atacado,
                 integra_atacado_muffato,
                 integra_desconto,
                 integra_desconto_cooperado,
                 integra_fidelidade,
                 integra_fidelidade_muffato,
                 integra_escalonada,
                 integra_combo,
                 integra_atacado_fidelidade,
                 integra_pack_desconto,
                 integra_cartao,
                 integra_cashback,
                 integra_cashback_porcentagem,
                 consinco_primeira_tela,
                 consinco_segunda_tela,
                 consinco_terceira_tela,
                 consinco_quarta_tela):
        self.client_id = client_id
        self.db_config_id = db_config_id
        self.forcar_campanha = forcar_campanha
        self.erp = erp
        self.log_info = log_info
        self.integra_normal = integra_normal
        self.integra_de_por = integra_de_por
        self.integra_pack_virtual = integra_pack_virtual
        self.integra_pack_cooperado = integra_pack_cooperado
        self.integra_pague_leve = integra_pague_leve
        self.integra_pague_leve_cooperado = integra_pague_leve_cooperado
        self.integra_atacado = integra_atacado
        self.integra_atacado_muffato = integra_atacado_muffato
        self.integra_desconto = integra_desconto
        self.integra_desconto_cooperado = integra_desconto_cooperado
        self.integra_fidelidade = integra_fidelidade
        self.integra_fidelidade_muffato = integra_fidelidade_muffato
        self.integra_escalonada = integra_escalonada
        self.integra_combo = integra_combo
        self.integra_atacado_fidelidade = integra_atacado_fidelidade
        self.integra_pack_desconto = integra_pack_desconto
        self.integra_cartao = integra_cartao
        self.integra_cashback = integra_cashback
        self.integra_cashback_porcentagem = integra_cashback_porcentagem
        self.consinco_gerenciador_precos = consinco_primeira_tela
        self.consinco_produtos_promocionais = consinco_segunda_tela
        self.consinco_regra_incentivo = consinco_terceira_tela
        self.consinco_monitor = consinco_quarta_tela

    @staticmethod
    def from_dict(dict_phase3: dict):
        return Phase3(
            dict_phase3['client_id'],
            dict_phase3['db_config_id'],
            dict_phase3['forcar_campanha'],
            dict_phase3['erp'],
            dict_phase3['log_info'],
            dict_phase3['integra_normal'],
            dict_phase3['integra_de_por'],
            dict_phase3['integra_pack_virtual'],
            dict_phase3['integra_pack_cooperado'],
            dict_phase3['integra_pague_leve'],
            dict_phase3['integra_pague_leve_cooperado'],
            dict_phase3['integra_atacado'],
            dict_phase3['integra_atacado_muffato'],
            dict_phase3['integra_desconto'],
            dict_phase3['integra_desconto_cooperado'],
            dict_phase3['integra_fidelidade'],
            dict_phase3['integra_fidelidade_muffato'],
            dict_phase3['integra_escalonada'],
            dict_phase3['integra_combo'],
            dict_phase3['integra_atacado_fidelidade'],
            dict_phase3['integra_pack_desconto'],
            dict_phase3['integra_cartao'],
            dict_phase3['integra_cashback'],
            dict_phase3['integra_cashback_porcentagem'],
            dict_phase3['consinco_gerenciador_precos'],
            dict_phase3['consinco_produtos_promocionais'],
            dict_phase3['consinco_regra_incentivo'],
            dict_phase3['consinco_monitor']
        )

