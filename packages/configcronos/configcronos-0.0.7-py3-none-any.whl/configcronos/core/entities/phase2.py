class Phase2:

    def __init__(self,
                 client_id,
                 db_config_id,
                 integrador_parcial,
                 forcar_campanha,
                 modo,
                 erp,
                 log_info,
                 modo_custo,
                 update_remoto,
                 gera_custo_verba,
                 integra_familia,
                 tipos_por_familia,
                 integra_associados,
                 tipos_por_associado,
                 pack_valor_brinde,
                 pague_leve_valor_brinde,
                 desconto_unidade_proporcional,
                 desconto_unidade_valor,
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
        self.integrador_parcial = integrador_parcial
        self.forcar_campanha = forcar_campanha
        self.modo = modo
        self.erp = erp
        self.log_info = log_info
        self.modo_custo = modo_custo
        self.update_remoto = update_remoto
        self.gera_custo_verba = gera_custo_verba
        self.integra_familia = integra_familia
        self.tipos_por_familia = tipos_por_familia
        self.integra_associados = integra_associados
        self.tipos_por_associado = tipos_por_associado
        self.pack_valor_brinde = pack_valor_brinde
        self.pague_leve_valor_brinde = pague_leve_valor_brinde
        self.desconto_unidade_proporcional = desconto_unidade_proporcional
        self.desconto_unidade_valor = desconto_unidade_valor
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
