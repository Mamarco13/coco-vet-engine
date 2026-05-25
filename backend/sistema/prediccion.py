from abc import ABC, abstractmethod
import modulos.moduloDemografico
import modulos.moduloClinico
import modulos.moduloLaboratorio

class Prediccion(ABC):
    #-----------------------------------------#
    #             CONSTRUCTORES               #       
    #-----------------------------------------#

    def __init__(self, moduloDemografico: modulos.moduloDemografico.ModuloDemografico=None,
                       moduloClinico: modulos.moduloClinico.ModuloClinico=None,
                       moduloLaboratorio: modulos.moduloLaboratorio.ModuloLaboratorio=None):
            self.moduloDemografico = moduloDemografico
            self.moduloClinico = moduloClinico
            self.moduloLaboratorio = moduloLaboratorio
    
    #-----------------------------------------#
    #                SETTERS                  #
    #-----------------------------------------#
    def establecer_moduloDemografico(self, moduloDemografico):
        self.moduloDemografico = moduloDemografico
    
    def establecer_moduloClinico(self, moduloClinico):
        self.moduloClinico = moduloClinico
    
    def establecer_moduloLaboratorio(self, moduloLaboratorio):
        self.moduloLaboratorio = moduloLaboratorio
    
    #-----------------------------------------#
    #            FUNCIONALIDADES              #
    #-----------------------------------------#
    @abstractmethod
    def fuzzificar_datos(self):
        pass
    
    @abstractmethod
    def implementar_reglas(self):
        pass
    
    @abstractmethod
    def predecir(self):
        pass
