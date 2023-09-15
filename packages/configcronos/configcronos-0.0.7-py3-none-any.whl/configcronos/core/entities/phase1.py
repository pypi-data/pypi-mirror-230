class Phase1:

    def __init__(self,
            smarket_payload_max_length,
            categories,
            competitors,
            coupons,
            families,
            products,
            products_associate,
            research_products,
            researches,
            segments,
            stores,
            stores_products,
            suppliers,
            gera_arquivo_envio,
            lojas_ignoradas,
            divisoes_ignoradas,
            segmentos_ignorados,
            parametros_imposto,
            parametros_custo_liquido,
            converte_percentual_proporcao,
            data_inicio_cupons,
            data_fim_cupons,
            tipo_categoria,
            quantidade_digitos_ean,
            carrega_aliquotas,
            dias_semana_carga,
            envia_notificacoes,
            envia_dados_api,
            endpoint_api_envio,
            endpoint_api_envio_authentication,
            fragmento_produto_loja) -> None:
        self.smarket_payload_max_length = smarket_payload_max_length
        self.categories = categories
        self.competitors = competitors
        self.coupons = coupons
        self.families = families
        self.products = products
        self.products_associate = products_associate
        self.research_products = research_products
        self.researches = researches
        self.segments = segments
        self.stores = stores
        self.stores_products = stores_products
        self.suppliers = suppliers
        self.gera_arquivo_envio = gera_arquivo_envio
        self.lojas_ignoradas = lojas_ignoradas
        self.divisoes_ignoradas = divisoes_ignoradas
        self.segmentos_ignorados = segmentos_ignorados
        self.parametros_imposto = parametros_imposto
        self.parametros_custo_liquido = parametros_custo_liquido
        self.converte_percentual_proporcao = converte_percentual_proporcao
        self.data_inicio_cupons = data_inicio_cupons
        self.data_fim_cupons = data_fim_cupons
        self.tipo_categoria = tipo_categoria
        self.quantidade_digitos_ean = quantidade_digitos_ean
        self.carrega_aliquotas = carrega_aliquotas
        self.dias_semana_carga = dias_semana_carga
        self.envia_notificacoes = envia_notificacoes
        self.envia_dados_api = envia_dados_api
        self.endpoint_api_envio = endpoint_api_envio
        self.endpoint_api_envio_authentication = endpoint_api_envio_authentication
        self.fragmento_produto_loja = fragmento_produto_loja

