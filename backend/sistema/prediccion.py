from abc import ABC, abstractmethod
from backend.modulos.moduloDemografico import ModuloDemografico
from backend.modulos.moduloClinico import ModuloClinico
from backend.modulos.moduloLaboratorio import ModuloLaboratorio

class Prediccion(ABC):
    #-----------------------------------------#
    #             CONSTRUCTORES               #       
    #-----------------------------------------#

    def __init__(self, moduloDemografico: ModuloDemografico = None,
                       moduloClinico: ModuloClinico = None,
                       moduloLaboratorio: ModuloLaboratorio = None):
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
