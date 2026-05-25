class ModuloLaboratorio:
    #-----------------------------------------#
    #             CONSTRUCTORES               #       
    #-----------------------------------------#
    
    def __init__(self, alp=None, usg=None, alt=None, colesterol=None):
        self.alp = alp
        self.usg = usg
        self.alt = alt
        self.colesterol = colesterol
    #-----------------------------------------#
    #                SETTERS                  #       
    #-----------------------------------------#
    def establecer_alp(self, alp):
        self.alp = alp

    def establecer_usg(self, usg):
        self.usg = usg
    
    def establecer_alt(self, alt):
        self.alt = alt
    
    def establecer_colesterol(self, colesterol):
        self.colesterol = colesterol

    #-----------------------------------------#
    #                GETTERS                  #       
    #-----------------------------------------#

    def obtener_alp(self):
        return self.alp

    def obtener_usg(self):
        return self.usg
    
    def obtener_alt(self):
        return self.alt
    
    def obtener_colesterol(self):
        return self.colesterol