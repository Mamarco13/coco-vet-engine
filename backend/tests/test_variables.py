"""!
@file test_variables.py
@brief Tests unitarios para FuzzyVariable.
"""

import pytest
import numpy as np
from logicaDifusa.variables import FuzzyVariable
from logicaDifusa.funcionesPertenencia import TriangularMF


# ======================================================
# FIXTURES
# ======================================================

@pytest.fixture
def universo():
    return np.arange(0, 1.01, 0.01)


@pytest.fixture
def variable(universo):
    return FuzzyVariable("test", universo)


@pytest.fixture
def mf_media(universo):
    return TriangularMF(universo, 0.2, 0.5, 0.8)


@pytest.fixture
def mf_baja(universo):
    return TriangularMF(universo, 0.0, 0.2, 0.4)


# ======================================================
# TESTS — ADD / GET / CONTAINS
# ======================================================

class TestAddGet:

    def test_add_y_get_membership(self, variable, mf_media):
        variable.add_membership("media", mf_media)
        assert variable.get_membership("media") is mf_media

    def test_getitem_equivalente_a_get(self, variable, mf_media):
        variable.add_membership("media", mf_media)
        assert variable["media"] is mf_media

    def test_contains_true(self, variable, mf_media):
        variable.add_membership("media", mf_media)
        assert "media" in variable

    def test_contains_false(self, variable):
        assert "inexistente" not in variable

    def test_etiqueta_duplicada_lanza_error(self, variable, mf_media):
        variable.add_membership("media", mf_media)
        with pytest.raises(ValueError, match="ya existe"):
            variable.add_membership("media", mf_media)

    def test_etiqueta_inexistente_lanza_error(self, variable):
        with pytest.raises(ValueError, match="No existe"):
            variable.get_membership("inexistente")


# ======================================================
# TESTS — FUZZIFY
# ======================================================

class TestFuzzify:

    def test_fuzzify_devuelve_todas_etiquetas(
        self, variable, mf_media, mf_baja
    ):
        variable.add_membership("media", mf_media)
        variable.add_membership("baja", mf_baja)
        result = variable.fuzzify(0.5)
        assert set(result.keys()) == {"media", "baja"}

    def test_fuzzify_pico_es_1(self, variable, mf_media):
        """El grado de pertenencia en el pico de trimf debe ser 1."""
        variable.add_membership("media", mf_media)
        result = variable.fuzzify(0.5)
        assert abs(result["media"] - 1.0) < 1e-6

    def test_fuzzify_fuera_de_soporte_es_0(self, variable, mf_media):
        """El grado de pertenencia fuera del soporte debe ser 0."""
        variable.add_membership("media", mf_media)
        result = variable.fuzzify(0.9)
        assert abs(result["media"] - 0.0) < 1e-6

    def test_fuzzify_flanco_ascendente(self, variable, mf_media):
        """A mitad del flanco ascendente la pertenencia debe ser ~0.5."""
        variable.add_membership("media", mf_media)
        result = variable.fuzzify(0.35)
        assert 0.45 < result["media"] < 0.55


# ======================================================
# TESTS — ETIQUETAS / LEN / REMOVE / CLEAR
# ======================================================

class TestManagement:

    def test_get_labels(self, variable, mf_media, mf_baja):
        variable.add_membership("media", mf_media)
        variable.add_membership("baja", mf_baja)
        etiquetas = variable.get_labels()
        assert "media" in etiquetas
        assert "baja" in etiquetas

    def test_len_vacio(self, variable):
        assert len(variable) == 0

    def test_len_con_memberships(self, variable, mf_media, mf_baja):
        variable.add_membership("media", mf_media)
        variable.add_membership("baja", mf_baja)
        assert len(variable) == 2

    def test_remove_membership(self, variable, mf_media):
        variable.add_membership("media", mf_media)
        variable.remove_membership("media")
        assert "media" not in variable

    def test_remove_inexistente_lanza_error(self, variable):
        with pytest.raises(ValueError):
            variable.remove_membership("inexistente")

    def test_clear_memberships(self, variable, mf_media, mf_baja):
        variable.add_membership("media", mf_media)
        variable.add_membership("baja", mf_baja)
        variable.clear_memberships()
        assert len(variable) == 0