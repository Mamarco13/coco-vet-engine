"""!
@file variables.py
@brief Implementación de variables lingüísticas difusas.

@details
Este módulo implementa las variables difusas
utilizadas por el sistema de inferencia difusa.

Una variable difusa está compuesta por:
    - Un nombre
    - Un universo de discurso
    - Múltiples funciones de pertenencia

Ejemplo:

    TEMPERATURA
        - Baja
        - Media
        - Alta

Arquitectura aplicada:
    - Patrón composición
"""

import matplotlib.pyplot as plt


class FuzzyVariable:
    """!
    @brief Representa una variable lingüística difusa.
    """

    def __init__(self, name, universe):
        """!
        @brief Constructor de variable difusa.

        @param name Nombre de la variable.
        @param universe Universo de discurso.
        """

        self.name = name
        self.universe = universe

        # Diccionario:
        # etiqueta -> membership function
        self.memberships = {}

    def add_membership(self, label, membership_function):
        """!
        @brief Añade una función de pertenencia.

        @param label Etiqueta lingüística.
        @param membership_function Función de pertenencia.
        """

        if label in self.memberships:
            raise ValueError(
                f"La etiqueta '{label}' ya existe"
            )

        self.memberships[label] = membership_function

    def get_membership(self, label):
        """!
        @brief Obtiene una función de pertenencia.

        @param label Etiqueta lingüística.
        @return Función de pertenencia asociada.
        """

        if label not in self.memberships:
            raise ValueError(
                f"No existe la etiqueta '{label}'"
            )

        return self.memberships[label]

    def fuzzify(self, value):
        """!
        @brief Fuzzifica un valor de entrada.

        @details
        Calcula el grado de pertenencia del valor
        para todas las etiquetas lingüísticas.

        @param value Valor de entrada.
        @return Diccionario etiqueta -> activación.
        """

        results = {}

        for label, membership in self.memberships.items():

            results[label] = membership.compute(value)

        return results

    def get_labels(self):
        """!
        @brief Devuelve las etiquetas lingüísticas.

        @return Lista de etiquetas.
        """

        return list(self.memberships.keys())

    def remove_membership(self, label):
        """!
        @brief Elimina una función de pertenencia.

        @param label Etiqueta lingüística.
        """

        if label not in self.memberships:
            raise ValueError(
                f"No existe la etiqueta '{label}'"
            )

        del self.memberships[label]

    def clear_memberships(self):
        """!
        @brief Elimina todas las memberships.
        """

        self.memberships.clear()

    def plot(self):
        """!
        @brief Visualiza la variable difusa.

        @details
        Representa gráficamente todas las
        funciones de pertenencia asociadas
        a la variable.
        """

        plt.figure(figsize=(8, 5))

        for label, membership in self.memberships.items():

            plt.plot(
                self.universe,
                membership.get_membership(),
                label=label
            )

        plt.title(self.name)

        plt.xlabel("Universo")

        plt.ylabel("Grado de pertenencia")

        plt.legend()

        plt.grid(True)

        plt.show()

    def __getitem__(self, label):
        """!
        @brief Permite acceder usando [].

        @example
        temperatura["alta"]

        @param label Etiqueta lingüística.
        @return Función de pertenencia.
        """

        return self.get_membership(label)

    def __contains__(self, label):
        """!
        @brief Comprueba si existe una etiqueta.

        @param label Etiqueta lingüística.
        @return True si existe.
        """

        return label in self.memberships

    def __len__(self):
        """!
        @brief Devuelve el número de memberships.

        @return Número de etiquetas lingüísticas.
        """

        return len(self.memberships)