"""!
@file defuzzification.py
@brief Métodos de defuzzificación fuzzy.

@details
Este módulo implementa distintos métodos
de defuzzificación para transformar una
salida fuzzy en un valor crisp.

Métodos soportados:
    - Centroid
    - Bisector
    - Mean of Maximum (MOM)
    - Smallest of Maximum (SOM)
    - Largest of Maximum (LOM)

Arquitectura aplicada:
    - Patrón estrategia
"""

from abc import ABC, abstractmethod
import skfuzzy as fuzz


class Defuzzifier(ABC):
    """!
    @brief Interfaz abstracta para defuzzificación.
    """

    @abstractmethod
    def compute(self, universe, membership):
        """!
        @brief Ejecuta defuzzificación.

        @param universe Universo de discurso.
        @param membership Membership agregada.
        @return Valor crisp.
        """
        pass


class CentroidDefuzzifier(Defuzzifier):
    """!
    @brief Método centroide.

    @details
    Calcula el centro de gravedad
    de la función fuzzy agregada.
    """

    def compute(self, universe, membership):

        return fuzz.defuzz(
            universe,
            membership,
            "centroid"
        )


class BisectorDefuzzifier(Defuzzifier):
    """!
    @brief Método bisector.

    @details
    Encuentra el punto que divide el área
    bajo la curva fuzzy en dos partes iguales.
    """

    def compute(self, universe, membership):

        return fuzz.defuzz(
            universe,
            membership,
            "bisector"
        )


class MOMDefuzzifier(Defuzzifier):
    """!
    @brief Mean Of Maximum.

    @details
    Calcula el promedio de los puntos máximos
    de la función fuzzy agregada.
    """

    def compute(self, universe, membership):

        return fuzz.defuzz(
            universe,
            membership,
            "mom"
        )


class SOMDefuzzifier(Defuzzifier):
    """!
    @brief Smallest Of Maximum.

    @details
    Encuentra el punto más pequeño entre los
    puntos máximos de la función fuzzy agregada.
    """

    def compute(self, universe, membership):

        return fuzz.defuzz(
            universe,
            membership,
            "som"
        )


class LOMDefuzzifier(Defuzzifier):
    """!
    @brief Largest Of Maximum.

    @details
    Encuentra el punto más grande entre los
    puntos máximos de la función fuzzy agregada.
    """

    def compute(self, universe, membership):

        return fuzz.defuzz(
            universe,
            membership,
            "lom"
        )