class ModuloClinico:
    #-----------------------------------------#
    #             CONSTRUCTORES               #       
    #-----------------------------------------#
    
    def __init__(self, polidipsia=None, abdomen_inflamado=None, alopecia=None, polifagia=None, poliuria=None, debilidad_muscular=None, piel_fina=None, jadeo=None):
        self.polidipsia = polidipsia
        self.abdomen_inflamado = abdomen_inflamado
        self.alopecia = alopecia
        self.polifagia = polifagia
        self.poliuria = poliuria
        self.debilidad_muscular = debilidad_muscular
        self.piel_fina = piel_fina
        self.jadeo = jadeo

    #-----------------------------------------#
    #                SETTERS                  #       
    #-----------------------------------------#
    def establecer_polidipsia(self, polidipsia):
        self.polidipsia = polidipsia

    def establecer_abdomen_inflamado(self, abdomen_inflamado):
        self.abdomen_inflamado = abdomen_inflamado

    def establecer_alopecia(self, alopecia):
        self.alopecia = alopecia

    def establecer_polifagia(self, polifagia):
        self.polifagia = polifagia

    def establecer_poliuria(self, poliuria):
        self.poliuria = poliuria

    def establecer_debilidad_muscular(self, debilidad_muscular):
        self.debilidad_muscular = debilidad_muscular

    def establecer_piel_fina(self, piel_fina):
        self.piel_fina = piel_fina

    def establecer_jadeo(self, jadeo):
        self.jadeo = jadeo

    #-----------------------------------------#
    #                GETTERS                  #       
    #-----------------------------------------#

    def obtener_polidipsia(self):
        return self.polidipsia

    def obtener_abdomen_inflamado(self):
        return self.abdomen_inflamado

    def obtener_alopecia(self):
        return self.alopecia

    def obtener_polifagia(self):
        return self.polifagia

    def obtener_poliuria(self):
        return self.poliuria

    def obtener_debilidad_muscular(self):
        return self.debilidad_muscular

    def obtener_piel_fina(self):
        return self.piel_fina

    def obtener_jadeo(self):
        return self.jadeo