"""!
@file test_sistema.py
@brief Tests unitarios para FuzzySystem.

@details
Cubre:
    - infer() devuelve todas las claves esperadas
    - crisp dentro del universo
    - confianza, fuerza y consenso entre 0 y 1
    - _get_label devuelve etiquetas correctas
    - _get_label hace clipping sin lanzar excepción
    - consenso = 1 cuando todas las reglas concuerdan
    - consenso < 1 cuando las reglas apuntan a términos distintos
    - sin reglas activas retorna resultado con confidence=0
"""

import pytest
import numpy as np
from logicaDifusa.variables import FuzzyVariable
from logicaDifusa.funcionesPertenencia import (
    TriangularMF,
    ZShapeMF,
    SShapeMF
)
from logicaDifusa.reglas import Rule, FuzzyOperator
from logicaDifusa.sistema import FuzzySystem


# ======================================================
# HELPERS / FIXTURES
# ======================================================

def output_riesgo():
    """Variable de salida idéntica a consecuente.json."""
    u = np.arange(0, 1.01, 0.01)
    var = FuzzyVariable("riesgo", u)
    var.add_membership("muy_bajo", ZShapeMF(u, 0.0, 0.06))
    var.add_membership("bajo",     TriangularMF(u, 0.02, 0.12, 0.24))
    var.add_membership("medio",    TriangularMF(u, 0.28, 0.50, 0.72))
    var.add_membership("alto",     TriangularMF(u, 0.76, 0.87, 0.94))
    var.add_membership("muy_alto", SShapeMF(u, 0.96, 1.0))
    return var


def regla_simple(term, weight=1.0):
    """Regla que activa 'term' cuando x=0.5 (pico)."""
    u = np.arange(0, 1.01, 0.01)
    mf = TriangularMF(u, 0.0, 0.5, 1.0)
    return Rule(
        antecedents=[("x", mf)],
        consequent=("riesgo", term),
        weight=weight
    )


@pytest.fixture
def sistema():
    return FuzzySystem()


@pytest.fixture
def output():
    return output_riesgo()


# ======================================================
# TESTS — infer() estructura del resultado
# ======================================================

class TestInferEstructura:

    def test_infer_contiene_todas_las_claves(self, sistema, output):
        sistema.add_rule(regla_simple("alto"))
        result = sistema.infer({"x": 0.5}, output)

        claves_esperadas = {
            "crisp", "label", "etiqueta",
            "confidence", "fuerza", "consenso",
            "rules", "aggregated"
        }

        assert claves_esperadas.issubset(result.keys())

    def test_crisp_dentro_del_universo(self, sistema, output):
        sistema.add_rule(regla_simple("alto"))
        result = sistema.infer({"x": 0.5}, output)
        assert 0.0 <= result["crisp"] <= 1.0

    def test_confidence_entre_0_y_1(self, sistema, output):
        sistema.add_rule(regla_simple("alto"))
        result = sistema.infer({"x": 0.5}, output)
        assert 0.0 <= result["confidence"] <= 1.0

    def test_fuerza_entre_0_y_1(self, sistema, output):
        sistema.add_rule(regla_simple("alto"))
        result = sistema.infer({"x": 0.5}, output)
        assert 0.0 <= result["fuerza"] <= 1.0

    def test_consenso_entre_0_y_1(self, sistema, output):
        sistema.add_rule(regla_simple("alto"))
        result = sistema.infer({"x": 0.5}, output)
        assert 0.0 <= result["consenso"] <= 1.0

    def test_rules_es_lista_no_vacia(self, sistema, output):
        sistema.add_rule(regla_simple("alto"))
        result = sistema.infer({"x": 0.5}, output)
        assert isinstance(result["rules"], list)
        assert len(result["rules"]) > 0


# ======================================================
# TESTS — _get_label
# ======================================================

class TestGetLabel:

    def test_label_muy_bajo_en_cero(self, sistema, output):
        label, etiqueta = sistema._get_label(output, 0.0)
        assert label == "muy_bajo"
        assert etiqueta == "Muy bajo"

    def test_label_bajo(self, sistema, output):
        label, _ = sistema._get_label(output, 0.12)
        assert label == "bajo"

    def test_label_medio(self, sistema, output):
        label, _ = sistema._get_label(output, 0.5)
        assert label == "medio"

    def test_label_alto(self, sistema, output):
        label, _ = sistema._get_label(output, 0.87)
        assert label == "alto"

    def test_label_muy_alto_en_uno(self, sistema, output):
        label, _ = sistema._get_label(output, 1.0)
        assert label == "muy_alto"

    def test_clipping_por_encima_no_lanza_error(self, sistema, output):
        """Valor por encima del universo: clipping silencioso."""
        label, _ = sistema._get_label(output, 1.5)
        assert label == "muy_alto"

    def test_clipping_por_debajo_no_lanza_error(self, sistema, output):
        """Valor por debajo del universo: clipping silencioso."""
        label, _ = sistema._get_label(output, -0.5)
        assert label == "muy_bajo"

    def test_etiqueta_capitalizada(self, sistema, output):
        _, etiqueta = sistema._get_label(output, 0.5)
        assert etiqueta[0].isupper()


# ======================================================
# TESTS — Confianza compuesta
# ======================================================

class TestConfianza:

    def test_consenso_1_cuando_todas_concuerdan(self, sistema, output):
        sistema.add_rule(regla_simple("alto"))
        sistema.add_rule(regla_simple("alto"))
        result = sistema.infer({"x": 0.5}, output)
        assert abs(result["consenso"] - 1.0) < 1e-6

    def test_consenso_menor_1_cuando_discrepan(self, sistema, output):
        sistema.add_rule(regla_simple("alto"))
        sistema.add_rule(regla_simple("muy_alto"))
        result = sistema.infer({"x": 0.5}, output)
        assert result["consenso"] < 1.0

    def test_reglas_fuertes_aumentan_fuerza(self, sistema, output):
        """Regla con activación máxima debe dar fuerza alta."""
        sistema.add_rule(regla_simple("alto"))
        result = sistema.infer({"x": 0.5}, output)
        # Con una sola regla al pico, fuerza debe ser alta
        assert result["fuerza"] > 0.8

    def test_peso_mayor_aumenta_influencia(self, sistema, output):
        """Regla con peso 2 debe dominar sobre regla con peso 1."""
        sistema.add_rule(regla_simple("alto",     weight=1.0))
        sistema.add_rule(regla_simple("muy_alto", weight=2.0))
        result = sistema.infer({"x": 0.5}, output)
        # El término dominante debe ser muy_alto (mayor peso)
        term_activations = {}
        for r in result["rules"]:
            _, term = r.consequent
            term_activations[term] = (
                term_activations.get(term, 0.0)
                + r.activation * r.rule.weight
            )
        assert term_activations["muy_alto"] > term_activations["alto"]


# ======================================================
# TESTS — Casos de error
# ======================================================

class TestErrores:

    def test_sin_reglas_activas_retorna_confianza_cero(self, sistema, output):
        """Sin reglas activas el sistema retorna un resultado válido con métricas a 0."""
        u = np.arange(0, 1.01, 0.01)
        mf = TriangularMF(u, 0.4, 0.5, 0.6)
        rule = Rule(
            antecedents=[("x", mf)],
            consequent=("riesgo", "alto")
        )
        sistema.add_rule(rule)

        result = sistema.infer({"x": 0.0}, output)  # x=0.0 no activa la MF [0.4, 0.5, 0.6]

        assert result["confidence"] == 0.0
        assert result["fuerza"] == 0.0
        assert result["consenso"] == 0.0
        assert result["rules"] == []
        assert "crisp" in result
        assert "label" in result

    def test_clear_rules_vacia_el_sistema(self, sistema, output):
        sistema.add_rule(regla_simple("alto"))
        sistema.clear_rules()
        assert len(sistema.rules) == 0