"""!
@file sistema.py
@brief Sistema de inferencia difusa.
 
@details
Este módulo implementa el motor principal del
sistema fuzzy.
 
Responsabilidades:
    - Almacenar reglas
    - Evaluar reglas
    - Calcular activaciones
    - Obtener reglas activas
    - Realizar inferencia fuzzy
 
Arquitectura aplicada:
    - Patrón composición
    - Patrón fachada
"""
 
from dataclasses import dataclass
import numpy as np
from .defuzzification import (
    CentroidDefuzzifier
)
 
@dataclass
class RuleResult:
    """!
    @brief Resultado de activación de una regla.
 
    @details
    Esta estructura almacena:
        - la regla evaluada
        - su activación
        - el consecuente asociado
    """
 
    rule: object
    activation: float
    consequent: str
 
 
class FuzzySystem:
    """!
    @brief Sistema principal de inferencia fuzzy.
    """
 
    def __init__(self):
        """!
        @brief Constructor del sistema.
        """
 
        self.rules = []
 
        self.defuzzifier = (
            CentroidDefuzzifier()
        )
 
    def add_rule(self, rule):
        """!
        @brief Añade una regla al sistema.
 
        @param rule Regla fuzzy.
        """
 
        self.rules.append(rule)
 
    def evaluate_rules(self, inputs):
        """!
        @brief Evalúa todas las reglas del sistema.
 
        @param inputs Diccionario de entradas.
        @return Lista de resultados de reglas.
        """
 
        results = []
 
        for rule in self.rules:
 
            activation = rule.evaluate(inputs)
 
            result = RuleResult(
                rule=rule,
                activation=activation,
                consequent=rule.consequent
            )
 
            results.append(result)
 
        return results
 
    def get_active_rules(self, inputs):
        """!
        @brief Obtiene únicamente reglas activas.
 
        @details
        Una regla se considera activa si su
        activación es mayor que cero.
 
        @param inputs Diccionario de entradas.
        @return Lista de reglas activas.
        """
 
        results = self.evaluate_rules(inputs)
 
        active_rules = []
 
        for result in results:
 
            if result.activation > 0:
                active_rules.append(result)
 
        return active_rules
    
    def _aggregate_outputs(
        self,
        active_rules,
        output_variable
    ):
        """!
        @brief Agrega salidas fuzzy.
 
        @details
        Implementa agregación Mamdani mediante:
            - implicación MIN
            - agregación MAX
 
        @param active_rules Reglas activas.
        @param output_variable Variable fuzzy de salida.
        @return Membership agregada.
        """
 
        aggregated = np.zeros_like(
            output_variable.universe,
            dtype=float
        )
 
        for result in active_rules:
 
            activation = result.activation
 
            _, term = result.consequent
 
            membership = output_variable[
                term
            ]
 
            consequent_mf = (
                membership.get_membership()
            )
 
            # ======================================
            # IMPLICACIÓN (MIN)
            # ======================================
 
            clipped = np.minimum(
                activation,
                consequent_mf
            )
 
            # ======================================
            # AGREGACIÓN (MAX)
            # ======================================
 
            aggregated = np.maximum(
                aggregated,
                clipped
            )
 
        return aggregated
 
    def _get_label(
        self,
        output_variable,
        crisp_value
    ):
        """!
        @brief Determina la etiqueta lingüística del valor crisp.
 
        @details
        Evalúa la pertenencia de `crisp_value` en cada término
        de la variable de salida y devuelve el término con mayor
        grado de pertenencia.
 
        Si el valor cae fuera del universo se recorta al rango
        [universe_min, universe_max] antes de interpolar.
 
        @param output_variable Variable fuzzy de salida.
        @param crisp_value Valor defuzzificado.
        @return Tupla (label, etiqueta):
            - label: clave interna (ej. "muy_alto")
            - etiqueta: texto legible (ej. "Muy alto")
        """
 
        universe = output_variable.universe
 
        # Clipping defensivo: si crisp cae fuera del universo
        crisp_value = float(
            np.clip(
                crisp_value,
                universe[0],
                universe[-1]
            )
        )
 
        best_term = None
        best_mu = -1.0
 
        for term_name in output_variable.memberships:
 
            mf_array = (
                output_variable[term_name]
                .get_membership()
            )
 
            # Interpolación para obtener pertenencia exacta
            mu = float(
                np.interp(
                    crisp_value,
                    universe,
                    mf_array
                )
            )
 
            if mu > best_mu:
                best_mu = mu
                best_term = term_name
 
        etiqueta = (
            best_term.replace("_", " ").capitalize()
            if best_term
            else "desconocido"
        )
 
        return best_term, etiqueta
 
    def infer(
        self,
        inputs,
        output_variable
    ):
        """!
        @brief Ejecuta inferencia fuzzy completa.
 
        @details
        Pipeline:
            - evaluación reglas
            - agregación Mamdani
            - defuzzificación centroid
 
        @param inputs Entradas del sistema.
        @param output_variable Variable fuzzy de salida.
        @return Resultado inferencia.
        """
 
        # ==========================================
        # REGLAS ACTIVAS
        # ==========================================
 
        active_rules = self.get_active_rules(
            inputs
        )
 
        if not active_rules:
 
            raise ValueError(
                "No hay reglas activas"
            )
 
        # ==========================================
        # AGREGACIÓN
        # ==========================================
 
        aggregated = self._aggregate_outputs(
            active_rules,
            output_variable
        )
 
        # ==========================================
        # DEFUZZIFICACIÓN
        # ==========================================
 
        crisp_value = self.defuzzifier.compute(
            output_variable.universe,
            aggregated
        )
 
        # ==========================================
        # CONFIANZA FUZZY COMPUESTA
        # ==========================================
 
        # --- FUERZA: media ponderada de activaciones ---
        # Refleja qué tan fuerte activaron las reglas
        # en conjunto, no solo la mejor.
        #
        # fuerza = sum(ai * wi) / sum(wi)
 
        weighted_activation = sum(
            r.activation * r.rule.weight
            for r in active_rules
        )
 
        # Media autoponderada: cada regla contribuye
        # proporcionalmente a su propia activacion.
        # Evita que reglas debiles diluyan reglas fuertes.
        #
        # fuerza = sum(ai^2 * wi) / sum(ai * wi)
 
        weighted_activation_sq = sum(
            (r.activation ** 2) * r.rule.weight
            for r in active_rules
        )
 
        fuerza = (
            weighted_activation_sq / weighted_activation
            if weighted_activation > 0
            else 0.0
        )
 
        # --- CONSENSO: acuerdo entre reglas activas ---
        # Fraccion de la activacion ponderada total
        # que apunta al termino consecuente dominante.
        # Penaliza cuando reglas apuntan a terminos
        # contradictorios (ej. alto y muy_alto).
        #
        # consenso = max_term_activation / sum(ai * wi)
 
        term_activation = {}
 
        for r in active_rules:
 
            _, term = r.consequent
 
            term_activation[term] = (
                term_activation.get(term, 0.0)
                + r.activation * r.rule.weight
            )
 
        dominant_activation = max(
            term_activation.values()
        )
 
        consenso = (
            dominant_activation / weighted_activation
            if weighted_activation > 0
            else 0.0
        )
 
        # --- CONFIANZA FINAL: fuerza x consenso ---
        # Alta solo cuando las reglas son fuertes Y concuerdan.
 
        confidence = fuerza * consenso
 
        # ==========================================
        # ETIQUETA LINGUISTICA
        # ==========================================
 
        label, etiqueta = self._get_label(
            output_variable,
            crisp_value
        )
 
        return {
            "crisp": crisp_value,
            "label": label,
            "etiqueta": etiqueta,
            "confidence": confidence,
            "fuerza": fuerza,
            "consenso": consenso,
            "rules": active_rules,
            "aggregated": aggregated
        }
 
    def clear_rules(self):
        """!
        @brief Elimina todas las reglas del sistema.
        """
 
        self.rules.clear()