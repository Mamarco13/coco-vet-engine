"""!
@file test_prediccion_cushing.py
@brief Tests para PrediccionCushing.

@details
Cubre:
    - _validar_y_clipear_inputs: clipping numérico
    - _validar_y_clipear_inputs: strings se omiten
    - _validar_metadata: campos obligatorios
    - _validar_variable: universo, términos, función, params
    - _validar_regla: antecedentes, consecuente, peso
    - predecir(): test de integración con la base de conocimiento real
"""

import pytest
import warnings
import numpy as np
from sistema.prediccionCushing import PrediccionCushing
from logicaDifusa.variables import FuzzyVariable
from modulos.moduloDemografico import ModuloDemografico
from modulos.moduloClinico import ModuloClinico
from modulos.moduloLaboratorio import ModuloLaboratorio


# ======================================================
# MOCKS DE MÓDULOS
# ======================================================

def demografico(**kwargs):
    defaults = {"edad": 10, "raza": "bichon_frise", "peso_rel": 100}
    defaults.update(kwargs)
    return ModuloDemografico(**defaults)


def clinico(**kwargs):
    defaults = dict(
        polidipsia=True, abdomen_inflamado=True, alopecia=True,
        poliuria=True, polifagia=True, debilidad_muscular=True,
        piel_fina=False, jadeo=True
    )
    defaults.update(kwargs)
    return ModuloClinico(**defaults)


def laboratorio(**kwargs):
    defaults = {"alp": 780, "alt": 220, "usg": 1.012, "colesterol": 410}
    defaults.update(kwargs)
    return ModuloLaboratorio(**defaults)


def predictor_completo(**kwargs):
    """Instancia lista para inferencia con la base de conocimiento real."""
    p = PrediccionCushing(
        moduloDemografico=demografico(**kwargs.get("demo", {})),
        moduloClinico=clinico(**kwargs.get("clin", {})),
        moduloLaboratorio=laboratorio(**kwargs.get("lab", {}))
    )
    p.fuzzificar_datos()
    p.implementar_reglas()
    return p


# ======================================================
# TESTS — Clipping de entradas
# ======================================================

class TestClipping:

    def setup_method(self):
        self.predictor = PrediccionCushing()
        universo = np.arange(0, 3001, 1, dtype=float)
        var = FuzzyVariable("alp", universo)
        self.predictor.variables["alp"] = var

    def test_valor_dentro_del_universo_no_cambia(self):
        inputs = {"alp": 1500.0}
        result = self.predictor._validar_y_clipear_inputs(inputs)
        assert result["alp"] == 1500.0

    def test_valor_por_encima_se_recorta(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = self.predictor._validar_y_clipear_inputs({"alp": 4000.0})
            assert result["alp"] == 3000.0
            assert len(w) == 1
            assert "Clipping" in str(w[0].message)

    def test_valor_por_debajo_se_recorta(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = self.predictor._validar_y_clipear_inputs({"alp": -50.0})
            assert result["alp"] == 0.0
            assert len(w) == 1

    def test_string_no_se_clipea(self):
        inputs = {"raza": "bichon_frise"}
        result = self.predictor._validar_y_clipear_inputs(inputs)
        assert result["raza"] == "bichon_frise"

    def test_variable_sin_universo_pasa_intacta(self):
        """Variable no registrada en self.variables pasa sin modificar."""
        inputs = {"variable_inexistente": 9999.0}
        result = self.predictor._validar_y_clipear_inputs(inputs)
        assert result["variable_inexistente"] == 9999.0

    def test_multiples_variables_solo_recorta_las_que_salen(self):
        universo2 = np.arange(0, 101, 1, dtype=float)
        self.predictor.variables["alt"] = FuzzyVariable("alt", universo2)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = self.predictor._validar_y_clipear_inputs({
                "alp": 4000.0,   # fuera
                "alt": 50.0      # dentro
            })
            assert result["alp"] == 3000.0
            assert result["alt"] == 50.0
            assert len(w) == 1  # solo un warning


# ======================================================
# TESTS — Validación de metadata
# ======================================================


class TestValidarMetadata:

    def setup_method(self):
        self.p = PrediccionCushing()

    def test_metadata_valida_no_lanza(self):
        datos = {
            "nombre": "Cushing",
            "version": "1.0",
            "autor": "Manuel Martínez Cobos",  # Añadido para que sea 100% válido
            "descripcion": "Sistema de predicción"
        }
        self.p._validar_metadata(datos, "metadata.json")  # no debe lanzar

    def test_falta_autor_lanza_error(self):
        datos = {"version": "1.0", "descripcion": "test"}
        with pytest.raises(ValueError, match="autor"):
            self.p._validar_metadata(datos, "metadata.json")

    def test_falta_version_lanza_error(self):
        # Añadimos "autor" para pasar la primera validación y que falle en "version"
        datos = {"nombre": "Cushing", "autor": "Manuel Martínez Cobos", "descripcion": "test"}
        with pytest.raises(ValueError, match="version"):
            self.p._validar_metadata(datos, "metadata.json")

    def test_falta_descripcion_lanza_error(self):
        # Añadimos "autor" para pasar la primera validación y que falle en "descripcion"
        datos = {"nombre": "Cushing", "autor": "Manuel Martínez Cobos", "version": "1.0"}
        with pytest.raises(ValueError, match="descripcion"):
            self.p._validar_metadata(datos, "metadata.json")

# ======================================================
# TESTS — Validación de variable
# ======================================================

class TestValidarVariable:

    def setup_method(self):
        self.p = PrediccionCushing()

    def _def_valida(self):
        return {
            "universo": [0, 100, 1],
            "terminos": {
                "bajo": {"funcion": "zmf", "params": [0, 30]},
                "alto": {"funcion": "smf", "params": [70, 100]}
            }
        }

    def test_definicion_valida_no_lanza(self):
        self.p._validar_variable("alp", self._def_valida(), "vars.json")

    def test_sin_universo_lanza_error(self):
        defn = self._def_valida()
        del defn["universo"]
        with pytest.raises(ValueError, match="universo"):
            self.p._validar_variable("alp", defn, "vars.json")

    def test_universo_con_longitud_incorrecta_lanza_error(self):
        defn = self._def_valida()
        defn["universo"] = [0, 100]  # faltan 3 elementos
        with pytest.raises(ValueError, match="3 elementos"):
            self.p._validar_variable("alp", defn, "vars.json")

    def test_sin_terminos_lanza_error(self):
        defn = self._def_valida()
        del defn["terminos"]
        with pytest.raises(ValueError, match="terminos"):
            self.p._validar_variable("alp", defn, "vars.json")

    def test_termino_sin_funcion_lanza_error(self):
        defn = self._def_valida()
        del defn["terminos"]["bajo"]["funcion"]
        with pytest.raises(ValueError, match="funcion"):
            self.p._validar_variable("alp", defn, "vars.json")

    def test_funcion_desconocida_lanza_error(self):
        defn = self._def_valida()
        defn["terminos"]["bajo"]["funcion"] = "gaussmf"
        with pytest.raises(ValueError, match="gaussmf"):
            self.p._validar_variable("alp", defn, "vars.json")

    def test_termino_sin_params_lanza_error(self):
        defn = self._def_valida()
        del defn["terminos"]["bajo"]["params"]
        with pytest.raises(ValueError, match="params"):
            self.p._validar_variable("alp", defn, "vars.json")

    def test_params_no_es_lista_lanza_error(self):
        defn = self._def_valida()
        defn["terminos"]["bajo"]["params"] = "0,30"
        with pytest.raises(ValueError, match="lista"):
            self.p._validar_variable("alp", defn, "vars.json")

    def test_variable_categorica_valida(self):
        defn = {
            "tipo": "categorica",
            "terminos": {
                "bichon": ["bichon_frise", "bichon"],
                "boxer":  ["boxer"]
            }
        }
        self.p._validar_variable("raza", defn, "vars.json")

    def test_variable_categorica_sin_terminos_lanza_error(self):
        defn = {"tipo": "categorica"}
        with pytest.raises(ValueError, match="terminos"):
            self.p._validar_variable("raza", defn, "vars.json")


# ======================================================
# TESTS — Validación de regla
# ======================================================

class TestValidarRegla:

    def setup_method(self):
        self.p = PrediccionCushing()

    def _regla_valida(self):
        return {
            "antecedentes": [
                {"variable": "alp", "termino": "alto"},
                {"variable": "alt", "termino": "elevado"}
            ],
            "consecuente": {"variable": "riesgo", "termino": "alto"},
            "conectiva": "AND",
            "peso": 1.0
        }

    def test_regla_valida_no_lanza(self):
        self.p._validar_regla(self._regla_valida(), 1, "reglas.json")

    def test_sin_antecedentes_lanza_error(self):
        regla = self._regla_valida()
        del regla["antecedentes"]
        with pytest.raises(ValueError, match="antecedentes"):
            self.p._validar_regla(regla, 1, "reglas.json")

    def test_antecedentes_no_es_lista_lanza_error(self):
        regla = self._regla_valida()
        regla["antecedentes"] = "alp=alto"
        with pytest.raises(ValueError, match="lista"):
            self.p._validar_regla(regla, 1, "reglas.json")

    def test_antecedente_sin_variable_lanza_error(self):
        regla = self._regla_valida()
        del regla["antecedentes"][0]["variable"]
        with pytest.raises(ValueError, match="variable"):
            self.p._validar_regla(regla, 1, "reglas.json")

    def test_antecedente_sin_termino_lanza_error(self):
        regla = self._regla_valida()
        del regla["antecedentes"][0]["termino"]
        with pytest.raises(ValueError, match="termino"):
            self.p._validar_regla(regla, 1, "reglas.json")

    def test_sin_consecuente_lanza_error(self):
        regla = self._regla_valida()
        del regla["consecuente"]
        with pytest.raises(ValueError, match="consecuente"):
            self.p._validar_regla(regla, 1, "reglas.json")

    def test_consecuente_sin_termino_lanza_error(self):
        regla = self._regla_valida()
        del regla["consecuente"]["termino"]
        with pytest.raises(ValueError, match="termino"):
            self.p._validar_regla(regla, 1, "reglas.json")

    def test_peso_negativo_lanza_error(self):
        regla = self._regla_valida()
        regla["peso"] = -1.0
        with pytest.raises(ValueError, match="negativo"):
            self.p._validar_regla(regla, 1, "reglas.json")

    def test_peso_no_numerico_lanza_error(self):
        regla = self._regla_valida()
        regla["peso"] = "alto"
        with pytest.raises(ValueError, match="numero"):
            self.p._validar_regla(regla, 1, "reglas.json")


# ======================================================
# TEST DE INTEGRACIÓN — predecir() end-to-end
# ======================================================

class TestIntegracion:

    def test_predecir_devuelve_claves_esperadas(self):
        p = predictor_completo()
        result = p.predecir()

        for clave in (
            "crisp", "label", "etiqueta",
            "confidence", "fuerza", "consenso"
        ):
            assert clave in result, f"Falta clave '{clave}' en resultado"

    def test_predecir_crisp_en_rango(self):
        p = predictor_completo()
        result = p.predecir()
        assert 0.0 <= result["crisp"] <= 1.0

    def test_predecir_label_valido(self):
        p = predictor_completo()
        result = p.predecir()
        etiquetas_validas = {
            "muy_bajo", "bajo", "medio", "alto", "muy_alto"
        }
        assert result["label"] in etiquetas_validas

    def test_predecir_caso_alto_riesgo(self):
        """Caso con todos los síntomas activos -> riesgo alto o muy_alto."""
        p = predictor_completo()
        result = p.predecir()
        assert result["label"] in {"alto", "muy_alto"}

    def test_predecir_caso_bajo_riesgo(self):
        """Caso sin síntomas y laboratorio normal -> riesgo bajo o muy_bajo."""
        p = predictor_completo(
            demo={"edad": 3, "raza": "otro", "peso_rel": 100},
            clin=dict(
                polidipsia=False, abdomen_inflamado=False, alopecia=False,
                poliuria=False, polifagia=False, debilidad_muscular=False,
                piel_fina=False, jadeo=False
            ),
            lab={"alp": 80, "alt": 40, "usg": 1.030, "colesterol": 180}
        )
        result = p.predecir()
        assert result["label"] in {"muy_bajo", "bajo", "medio"}

    def test_predecir_confidence_entre_0_y_1(self):
        p = predictor_completo()
        result = p.predecir()
        assert 0.0 <= result["confidence"] <= 1.0