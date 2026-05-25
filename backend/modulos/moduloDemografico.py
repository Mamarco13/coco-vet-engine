class ModuloDemografico:
    #-----------------------------------------#
    #             CONSTRUCTORES               #       
    #-----------------------------------------#
    
    def __init__(self, edad=None, raza=None, peso_rel=None):
        self.edad = edad
        self.raza = raza
        self.peso_rel = peso_rel
    
    #-----------------------------------------#
    #                SETTERS                  #       
    #-----------------------------------------#
    def establecer_edad(self, edad):
        self.edad = edad
    
    def establecer_raza(self, raza):
        self.raza = raza
    
    def establecer_peso_rel(self, peso_rel):
        self.peso_rel = peso_rel
    
    #-----------------------------------------#
    #                GETTERS                  #       
    #-----------------------------------------#

    def obtener_edad(self):
        return self.edad

    def obtener_raza(self):
        return self.raza

    def obtener_peso_rel(self):
        return self.peso_rel