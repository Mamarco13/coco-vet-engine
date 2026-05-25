"""!
@file funcionesPertenencia.py
@brief Implementación de funciones de pertenencia adaptativas.

@details
Este módulo implementa una capa de abstracción sobre la librería
skfuzzy para permitir el uso de funciones de pertenencia
parametrizables y adaptativas dentro de nuestro sistema de lógica difusa.

Arquitectura implementada:
    - Patrón estrategia
    - Polimorfismo mediante herencia
    - Template Method parcial

Librería base utilizada:
    - scikit-fuzzy
"""

from abc import ABC, abstractmethod
import numpy as np
import skfuzzy as fuzz


class MembershipFunction(ABC):
    """!
    @brief Interfaz abstracta para funciones de pertenencia.

    Esta clase define el comportamiento común que debe implementar
    cualquier función de pertenencia del sistema difuso.
    """

    @abstractmethod
    def compute(self, x):
        """!
        @brief Calcula el grado de pertenencia de un valor.

        @param x Valor de entrada.
        @return Grado de pertenencia del valor.
        """
        pass

    @abstractmethod
    def get_membership(self):
        """!
        @brief Devuelve el array completo de pertenencia.

        @return Array con los valores de pertenencia.
        """
        pass

    @abstractmethod
    def update(self, params):
        """!
        @brief Actualiza los parámetros de la función.

        @param params Nuevos parámetros.
        """
        pass

    @abstractmethod
    def validate(self, params):
        """!
        @brief Valida los parámetros de la función.

        @param params Parámetros a validar.
        """
        pass


class ParametricMF(MembershipFunction):
    """!
    @brief Clase base para funciones parametrizables.

    @details
    Esta clase implementa el comportamiento común de todas
    las funciones de pertenencia parametrizadas:
        - almacenamiento de parámetros
        - interpolación
        - actualización
        - cacheado de memberships

    Las subclases únicamente deben implementar:
        - get_membership()
        - validate()
    """

    def __init__(self, universe, params):
        """!
        @brief Constructor base.

        @param universe Universo de discurso.
        @param params Parámetros iniciales.
        """

        self.universe = universe

        self.validate(params)

        self.params = np.array(params, dtype=float)

        # Cache de la función de pertenencia
        self.membership_values = self.get_membership()

    def compute(self, x):
        """!
        @brief Calcula el grado de pertenencia de x.

        @param x Valor de entrada.
        @return Grado de pertenencia.
        """

        return fuzz.interp_membership(
            self.universe,
            self.membership_values,
            x
        )

    def update(self, params):
        """!
        @brief Actualiza parámetros y recalcula cache.

        @param params Nuevos parámetros.
        """

        self.validate(params)

        self.params = np.array(params, dtype=float)

        self.membership_values = self.get_membership()


class TriangularMF(ParametricMF):
    """!
    @brief Función de pertenencia triangular.

    @details
    Definida mediante tres parámetros:

        - a: inicio
        - b: pico
        - c: final

    Restricción:

    a < b < c
    """

    def __init__(self, universe, a, b, c):

        super().__init__(
            universe,
            [a, b, c]
        )

    def get_membership(self):
        """!
        @brief Genera la función triangular.

        @return Array de pertenencia triangular.
        """

        return fuzz.trimf(
            self.universe,
            self.params
        )

    def validate(self, params):
        """!
        @brief Valida parámetros triangulares.

        @param params Parámetros a validar.
        """

        if len(params) != 3:
            raise ValueError(
                "TriangularMF necesita 3 parámetros"
            )

        a, b, c = params

        if not (a <= b <= c):
            raise ValueError(
                "Debe cumplirse a <= b <= c"
            )


class TrapezoidalMF(ParametricMF):
    """!
    @brief Función de pertenencia trapezoidal.

    @details
    Definida mediante cuatro parámetros:

        - a: inicio
        - b: comienzo de meseta
        - c: final de meseta
        - d: final

    Restricción:

    a < b < c < d
    """

    def __init__(self, universe, a, b, c, d):

        super().__init__(
            universe,
            [a, b, c, d]
        )

    def get_membership(self):
        """!
        @brief Genera la función trapezoidal.

        @return Array de pertenencia trapezoidal.
        """

        return fuzz.trapmf(
            self.universe,
            self.params
        )

    def validate(self, params):
        """!
        @brief Valida parámetros trapezoidales.

        @param params Parámetros a validar.
        """

        if len(params) != 4:
            raise ValueError(
                "TrapezoidalMF necesita 4 parámetros"
            )

        a, b, c, d = params

        if not (a <= b <= c <= d):
            raise ValueError(
                "Debe cumplirse a <= b <= c <= d"
            )


class ZShapeMF(ParametricMF):
    """!
    @brief Función de pertenencia en forma de Z.

    @details
    Definida mediante dos parámetros:
        - a
        - b

    Restricción:

    a < b
    """

    def __init__(self, universe, a, b):

        super().__init__(
            universe,
            [a, b]
        )

    def get_membership(self):
        """!
        @brief Genera la función Z.

        @return Array de pertenencia Z.
        """

        return fuzz.zmf(
            self.universe,
            self.params[0],
            self.params[1]
        )

    def validate(self, params):
        """!
        @brief Valida parámetros Z.

        @param params Parámetros a validar.
        """

        if len(params) != 2:
            raise ValueError(
                "ZShapeMF necesita 2 parámetros"
            )

        a, b = params

        if not (a < b):
            raise ValueError(
                "Debe cumplirse a < b"
            )


class SShapeMF(ParametricMF):
    """!
    @brief Función de pertenencia en forma de S.

    @details
    Definida mediante dos parámetros:
        - a
        - b

    Restricción:

    a < b
    """

    def __init__(self, universe, a, b):

        super().__init__(
            universe,
            [a, b]
        )

    def get_membership(self):
        """!
        @brief Genera la función S.

        @return Array de pertenencia S.
        """

        return fuzz.smf(
            self.universe,
            self.params[0],
            self.params[1]
        )

    def validate(self, params):
        """!
        @brief Valida parámetros S.

        @param params Parámetros a validar.
        """

        if len(params) != 2:
            raise ValueError(
                "SShapeMF necesita 2 parámetros"
            )

        a, b = params

        if not (a < b):
            raise ValueError(
                "Debe cumplirse a < b"
            )