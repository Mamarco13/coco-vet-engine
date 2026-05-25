"""!
@file reglas.py
@brief Implementación de reglas difusas.

@details
Este módulo implementa las reglas fuzzy utilizadas
por el sistema de inferencia difusa.

Cada regla está compuesta por:
    - Antecedentes
    - Consecuente
    - Operador lógico
    - Peso

Arquitectura aplicada:
    - Patrón composición
    - Patrón estrategia
"""

from enum import Enum
import numpy as np


class FuzzyOperator(Enum):
    """!
    @brief Operadores lógicos fuzzy.
    """

    AND = "AND"
    OR = "OR"


class Rule:
    """!
    @brief Representa una regla difusa.

    @details
    Una regla fuzzy tiene la forma:

        IF antecedente THEN consecuente

    Ejemplo:

        IF temperatura IS alta
        AND humedad IS baja
        THEN ventilador IS rapido

    La activación de la regla se calcula utilizando
    los grados de pertenencia de los antecedentes
    y un operador lógico fuzzy.

    Para un operador AND:

        activacion = min(mu1, mu2, ..., mun)

    Posteriormente se aplica el peso de la regla:

        activacion_final = activacion * peso

    Ejemplo de cálculo:

        mu_temperatura_alta = 0.8
        mu_humedad_baja = 0.6

        activacion = min(0.8, 0.6)
                    = 0.6

        peso = 0.9

        activacion_final = 0.6 * 0.9
                        = 0.54

    Esto permite ajustar la importancia relativa
    de cada regla dentro del sistema difuso.
    """

    def __init__(
        self,
        antecedents,
        consequent,
        operator=FuzzyOperator.AND,
        weight=1.0
    ):
        """!
        @brief Constructor de regla.

        @param antecedents Lista de antecedentes.
        @param consequent Consecuente de la regla.
        @param operator Operador lógico fuzzy.
        @param weight Peso de la regla.
        """

        self.antecedents = antecedents
        self.consequent = consequent
        self.operator = operator
        self.weight = weight

    def evaluate(self, inputs):
        """!
        @brief Evalúa la activación de la regla.

        @details
        Calcula el grado de activación de la regla
        utilizando los valores de entrada y las
        funciones de pertenencia de los antecedentes.

        @param inputs Diccionario con valores de entrada.
        @return Activación final de la regla.
        """

        activations = []

        for variable_name, membership_function in self.antecedents:

            if variable_name not in inputs:
                raise ValueError(
                    f"Falta input para '{variable_name}'"
                )

            input_value = inputs[variable_name]

            activation = membership_function.compute(
                input_value
            )

            activations.append(activation)

        combined_activation = self._combine(
            activations
        )

        return combined_activation * self.weight

    def _combine(self, activations):
        """!
        @brief Combina activaciones fuzzy.

        @details
        Implementa operadores lógicos fuzzy:
            - AND -> mínimo
            - OR -> máximo

        @param activations Lista de activaciones.
        @return Activación combinada.
        """

        if self.operator == FuzzyOperator.AND:
            return np.min(activations)

        elif self.operator == FuzzyOperator.OR:
            return np.max(activations)

        else:
            raise ValueError(
                "Operador fuzzy no soportado"
            )

    def set_weight(self, weight):
        """!
        @brief Actualiza el peso de la regla.

        @param weight Nuevo peso.
        """

        if weight < 0:
            raise ValueError(
                "El peso no puede ser negativo"
            )

        self.weight = weight

    def get_weight(self):
        """!
        @brief Devuelve el peso actual.

        @return Peso de la regla.
        """

        return self.weight