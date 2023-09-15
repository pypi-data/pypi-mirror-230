class Segment:

    def __init__(self, tipo_segmento, regra):
        self.tipo_segmento = tipo_segmento
        self.regra = regra

    @property
    def localizador_regra(self) -> tuple[dict[str], str]:

        regras = {}
        if self.regra == 'LOJA':
            for tipo_oferta in self.tipo_segmento.keys():
                regras[tipo_oferta] = {}
                for segmento in self.tipo_segmento[tipo_oferta].keys():
                    for loja in self.tipo_segmento[tipo_oferta][segmento]:
                        if loja not in regras[tipo_oferta]:
                            regras[tipo_oferta][loja] = [segmento]
                        else:
                            regras[tipo_oferta][loja].append(segmento)

        elif self.regra == 'TIPO_OFERTA' or self.regra == 'MISTO':
            for tipo_oferta in self.tipo_segmento.keys():
                regras[tipo_oferta] = []
                for loja in self.tipo_segmento[tipo_oferta]:
                    if loja not in regras[tipo_oferta]:
                        regras[tipo_oferta].append(loja)

        elif self.regra == 'CAMPANHA':
            regras = {}

        return regras, self.regra
