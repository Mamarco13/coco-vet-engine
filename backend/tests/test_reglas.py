"""!
@file test_reglas.py
@brief Tests unitarios para Rule y FuzzyOperator.
"""

import pytest
import numpy as np
from logicaDifusa.variables import FuzzyVariable
from logicaDifusa.funcionesPertenencia import TriangularMF
from logicaDifusa.reglas import Rule, FuzzyOperator


# HELPERS

def crear_antecedente(nombre, a, b, c, term="activo"):
    """Crea una tupla (nombre_variable, membership_function)."""
    universo = np.arange(0, 1.01, 0.01)
    mf = TriangularMF(universo, a, b, c)
    return nombre, mf


# TESTS — OPERADOR AND

class TestAND:

    def test_and_devuelve_minimo(self):
        """AND fuzzy = mínimo de activaciones."""
        # v1=0.5 -> mu=1.0 (pico), v2=0.25 -> mu=0.5 (flanco)
        nombre1, mf1 = crear_antecedente("v1", 0.0, 0.5, 1.0)
        nombre2, mf2 = crear_antecedente("v2", 0.0, 0.5, 1.0)

        rule = Rule(
            antecedents=[(nombre1, mf1), (nombre2, mf2)],
            consequent=("riesgo", "alto"),
            operator=FuzzyOperator.AND
        )

        result = rule.evaluate({"v1": 0.5, "v2": 0.25})

        assert abs(result - 0.5) < 0.05

    def test_and_ambas_activas_al_maximo(self):
        nombre1, mf1 = crear_antecedente("v1", 0.0, 0.5, 1.0)
        nombre2, mf2 = crear_antecedente("v2", 0.0, 0.5, 1.0)

        rule = Rule(
            antecedents=[(nombre1, mf1), (nombre2, mf2)],
            consequent=("riesgo", "alto"),
            operator=FuzzyOperator.AND
        )

        result = rule.evaluate({"v1": 0.5, "v2": 0.5})

        assert abs(result - 1.0) < 1e-6

    def test_and_una_inactiva_devuelve_cero(self):
        nombre1, mf1 = crear_antecedente("v1", 0.0, 0.5, 1.0)
        nombre2, mf2 = crear_antecedente("v2", 0.3, 0.5, 0.7)

        rule = Rule(
            antecedents=[(nombre1, mf1), (nombre2, mf2)],
            consequent=("riesgo", "alto"),
            operator=FuzzyOperator.AND
        )

        # v2=0.0 está fuera del soporte [0.3, 0.7] -> mu=0
        result = rule.evaluate({"v1": 0.5, "v2": 0.0})

        assert abs(result - 0.0) < 1e-6


# TESTS — OPERADOR OR

class TestOR:

    def test_or_devuelve_maximo(self):
        """OR fuzzy = máximo de activaciones."""
        nombre1, mf1 = crear_antecedente("v1", 0.0, 0.5, 1.0)
        nombre2, mf2 = crear_antecedente("v2", 0.0, 0.5, 1.0)

        rule = Rule(
            antecedents=[(nombre1, mf1), (nombre2, mf2)],
            consequent=("riesgo", "alto"),
            operator=FuzzyOperator.OR
        )

        # v1=0.5 -> mu=1.0, v2=0.25 -> mu~0.5
        result = rule.evaluate({"v1": 0.5, "v2": 0.25})

        assert abs(result - 1.0) < 1e-6

    def test_or_ambas_inactivas_devuelve_cero(self):
        nombre1, mf1 = crear_antecedente("v1", 0.3, 0.5, 0.7)
        nombre2, mf2 = crear_antecedente("v2", 0.3, 0.5, 0.7)

        rule = Rule(
            antecedents=[(nombre1, mf1), (nombre2, mf2)],
            consequent=("riesgo", "alto"),
            operator=FuzzyOperator.OR
        )

        result = rule.evaluate({"v1": 0.0, "v2": 0.0})

        assert abs(result - 0.0) < 1e-6


# TESTS — PESO

class TestPeso:

    def test_peso_escala_activacion(self):
        """La activación final es activación_base × peso."""
        nombre, mf = crear_antecedente("v1", 0.0, 0.5, 1.0)

        rule = Rule(
            antecedents=[(nombre, mf)],
            consequent=("riesgo", "alto"),
            weight=0.5
        )

        # v1=0.5 -> mu=1.0, peso=0.5 -> activación=0.5
        result = rule.evaluate({"v1": 0.5})

        assert abs(result - 0.5) < 1e-6

    def test_peso_2_duplica_activacion(self):
        nombre, mf = crear_antecedente("v1", 0.0, 0.5, 1.0)

        rule = Rule(
            antecedents=[(nombre, mf)],
            consequent=("riesgo", "alto"),
            weight=2.0
        )

        # mu=1.0 * peso=2.0 -> activación=2.0
        result = rule.evaluate({"v1": 0.5})

        assert abs(result - 2.0) < 1e-6

    def test_set_weight_actualiza(self):
        rule = Rule(
            antecedents=[],
            consequent=("riesgo", "alto"),
            weight=1.0
        )
        rule.set_weight(0.7)
        assert rule.get_weight() == 0.7

    def test_peso_negativo_lanza_error(self):
        rule = Rule(antecedents=[], consequent=("riesgo", "alto"))
        with pytest.raises(ValueError):
            rule.set_weight(-0.1)


# TESTS — ERRORES DE EVALUACIÓN

class TestErrores:

    def test_input_faltante_lanza_error(self):
        nombre, mf = crear_antecedente("v1", 0.0, 0.5, 1.0)
        rule = Rule(
            antecedents=[(nombre, mf)],
            consequent=("riesgo", "alto")
        )
        with pytest.raises(ValueError, match="Falta input"):
            rule.evaluate({})

    def test_una_regla_sin_antecedentes_activa_con_peso(self):
        """Regla vacía: _combine([]) -> min([]) podría fallar."""
        rule = Rule(
            antecedents=[],
            consequent=("riesgo", "alto"),
            weight=1.0
        )
        # No debe lanzar excepción
        with pytest.raises(Exception):
            rule.evaluate({})