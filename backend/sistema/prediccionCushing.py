"""!
@file prediccionCushing.py
@brief Sistema de predicción difusa para síndrome de Cushing.

@details
Este módulo implementa un sistema de predicción
basado en lógica difusa utilizando el framework
fuzzy adaptativo desarrollado sobre scikit-fuzzy.

Responsabilidades:
    - Cargar base de conocimiento JSON
    - Crear variables fuzzy
    - Crear memberships
    - Construir reglas fuzzy
    - Ejecutar inferencia
    - Generar predicción

Arquitectura aplicada:
    - Patrón Composición
    - Patrón Fachada
"""

from .prediccion import Prediccion

from modulos.moduloDemografico import ModuloDemografico
from modulos.moduloClinico import ModuloClinico
from modulos.moduloLaboratorio import ModuloLaboratorio

from logicaDifusa.variables import FuzzyVariable

from logicaDifusa.funcionesPertenencia import (
    TriangularMF,
    ZShapeMF,
    SShapeMF
)

from logicaDifusa.reglas import (
    Rule,
    FuzzyOperator
)

from logicaDifusa.sistema import FuzzySystem

import json
import os
import numpy as np
import glob
import warnings


class CategoricalMF:
    """Función de pertenencia crisp para variables categóricas."""

    def __init__(self, accepted_values):
        self.accepted_values = {
            self._normalize(v)
            for v in accepted_values
        }

    def _normalize(self, value):
        if value is None:
            return ""

        return (
            str(value)
            .strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )

    def compute(self, x):
        return 1.0 if self._normalize(x) in self.accepted_values else 0.0


class PrediccionCushing(Prediccion):

    FUNCIONES_FUZZY = {
        "trimf": TriangularMF,
        "zmf": ZShapeMF,
        "smf": SShapeMF
    }

    def __init__(
        self,
        moduloDemografico: ModuloDemografico = None,
        moduloClinico: ModuloClinico = None,
        moduloLaboratorio: ModuloLaboratorio = None
    ):
        """!
        @brief Constructor del predictor.
        """

        super().__init__(
            moduloDemografico,
            moduloClinico,
            moduloLaboratorio
        )

        self.base_conocimiento_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'conocimiento',
            'cushing'
        )

        self._base_conocimiento = None

        # Sistema fuzzy principal
        self.system = FuzzySystem()

        # Variables fuzzy
        self.variables = {}

    # =====================================================
    # BASE DE CONOCIMIENTO
    # =====================================================

    def _cargar_base_conocimiento(self):
        """!
        @brief Carga la base de conocimiento modular.

        @details
        Carga automáticamente:
            - metadata
            - variables fuzzy
            - reglas fuzzy

        La estructura esperada es:

            conocimiento/
                cushing/
                    metadata.json
                    variables/
                    reglas/
        """

        if self._base_conocimiento is not None:
            return self._base_conocimiento

        base = {
            "metadata": {},
            "variables": {
                "antecedentes": {},
                "consecuentes": {}
            },
            "reglas": []
        }

        # =====================================================
        # METADATA
        # =====================================================

        metadata_path = os.path.join(
            self.base_conocimiento_path,
            "metadata.json"
        )

        with open(
            metadata_path,
            "r",
            encoding="utf-8"
        ) as archivo:

            loaded = json.load(archivo)
            base["metadata"] = loaded.get("metadata", loaded)

            self._validar_metadata(
                base["metadata"],
                metadata_path
            )

        # =====================================================
        # VARIABLES
        # =====================================================

        variables_path = os.path.join(
            self.base_conocimiento_path,
            "variables"
        )

        archivos_variables = glob.glob(
            os.path.join(
                variables_path,
                "*.json"
            )
        )

        for archivo_variable in archivos_variables:

            with open(
                archivo_variable,
                "r",
                encoding="utf-8"
            ) as archivo:

                contenido = json.load(
                    archivo
                )

            for var_nombre, var_def in contenido.items():
                self._validar_variable(
                    var_nombre,
                    var_def,
                    archivo_variable
                )

            nombre_archivo = os.path.basename(
                archivo_variable
            )

            # ==========================================
            # CONSECUENTES
            # ==========================================

            if "consecuente" in nombre_archivo:

                base["variables"][
                    "consecuentes"
                ].update(
                    contenido
                )

            # ==========================================
            # ANTECEDENTES
            # ==========================================

            else:

                base["variables"][
                    "antecedentes"
                ].update(
                    contenido
                )

        # =====================================================
        # REGLAS
        # =====================================================

        reglas_path = os.path.join(
            self.base_conocimiento_path,
            "reglas"
        )

        archivos_reglas = glob.glob(
            os.path.join(
                reglas_path,
                "*.json"
            )
        )

        for archivo_regla in archivos_reglas:

            with open(
                archivo_regla,
                "r",
                encoding="utf-8"
            ) as archivo:

                contenido = json.load(
                    archivo
                )

            # Si el archivo contiene múltiples reglas
            if isinstance(
                contenido,
                list
            ):

                for idx, regla in enumerate(contenido):
                    self._validar_regla(
                        regla,
                        idx + 1,
                        archivo_regla
                    )

                base["reglas"].extend(
                    contenido
                )

            # Si contiene una sola regla
            else:

                self._validar_regla(
                    contenido,
                    1,
                    archivo_regla
                )

                base["reglas"].append(
                    contenido
                )

        self._base_conocimiento = base

        return base

    # =====================================================
    # UNIVERSOS
    # =====================================================

    def _crear_universo(self, universo):
        """!
        @brief Genera universo numpy.

        @param universo Lista [inicio, fin, paso].
        @return Universo numpy.
        """

        inicio, fin, paso = universo

        return np.arange(
            inicio,
            fin + paso,
            paso
        )

    # =====================================================
    # VARIABLES FUZZY
    # =====================================================

    def _crear_variable_fuzzy(
        
        self,
        nombre,
        definicion
    ):
        """!
        @brief Crea una variable fuzzy.

        @param nombre Nombre de variable.
        @param definicion Definición JSON.
        @return Variable fuzzy creada.
        """
        # ==========================================
        # VARIABLES CATEGÓRICAS
        # ==========================================

        if definicion.get(
            "tipo",
            "numerica"
        ) == "categorica":

            variable = FuzzyVariable(
                nombre,
                np.array([0.0, 1.0])
            )

            terminos = definicion.get(
                "terminos",
                {}
            )

            for nombre_termino, valores in terminos.items():

                if not isinstance(valores, list):
                    raise ValueError(
                        f"Termino categorico invalido en '{nombre}': "
                        f"{nombre_termino}"
                    )

                membership = CategoricalMF(
                    valores
                )

                variable.add_membership(
                    nombre_termino,
                    membership
                )

            return variable

        universo = self._crear_universo(
            definicion["universo"]
        )

        variable = FuzzyVariable(
            nombre,
            universo
        )

        terminos = definicion.get(
            "terminos",
            {}
        )

        for nombre_termino, termino in terminos.items():

            nombre_funcion = termino.get(
                "funcion"
            )

            params = termino.get(
                "params",
                []
            )

            clase_fuzzy = self.FUNCIONES_FUZZY.get(
                nombre_funcion
            )

            if clase_fuzzy is None:
                raise ValueError(
                    f"Funcion fuzzy no soportada: "
                    f"{nombre_funcion}"
                )

            membership = clase_fuzzy(
                universo,
                *params
            )

            variable.add_membership(
                nombre_termino,
                membership
            )

        return variable

    # =====================================================
    # FUZZIFICACIÓN
    # =====================================================

    def fuzzificar_datos(self):
        """!
        @brief Construye todas las variables fuzzy.
        """

        base = self._cargar_base_conocimiento()

        variables_json = base.get(
            "variables",
            {}
        )

        antecedentes = variables_json.get(
            "antecedentes",
            {}
        )

        consecuentes = variables_json.get(
            "consecuentes",
            {}
        )

        # Antecedentes
        for nombre, definicion in antecedentes.items():

            variable = self._crear_variable_fuzzy(
                nombre,
                definicion
            )

            self.variables[nombre] = variable

            setattr(
                self,
                nombre,
                variable
            )

        # Consecuentes
        for nombre, definicion in consecuentes.items():

            variable = self._crear_variable_fuzzy(
                nombre,
                definicion
            )

            self.variables[nombre] = variable

            setattr(
                self,
                nombre,
                variable
            )

    # =====================================================
    # REGLAS
    # =====================================================

    def implementar_reglas(self):
        """!
        @brief Construye reglas fuzzy.
        """

        base = self._cargar_base_conocimiento()

        reglas_json = base.get(
            "reglas",
            []
        )

        for regla_json in reglas_json:

            antecedentes_json = regla_json.get(
                "antecedentes",
                []
            )

            antecedents = []

            for antecedente in antecedentes_json:

                variable_name = antecedente[
                    "variable"
                ]

                termino = antecedente[
                    "termino"
                ]

                variable = self.variables[
                    variable_name
                ]

                membership = variable[
                    termino
                ]

                antecedents.append(
                    (
                        variable_name,
                        membership
                    )
                )

            consecuente_json = regla_json[
                "consecuente"
            ]

            consequent_variable = consecuente_json[
                "variable"
            ]

            consequent_term = consecuente_json[
                "termino"
            ]

            operador = regla_json.get(
                "conectiva",
                regla_json.get(
                    "tipo",
                    "AND"
                )
            ).upper()

            if operador == "OR":

                fuzzy_operator = (
                    FuzzyOperator.OR
                )

            else:

                fuzzy_operator = (
                    FuzzyOperator.AND
                )

            peso = regla_json.get(
                "peso",
                1.0
            )

            label_text = regla_json.get("label")

            nueva_regla = Rule(
                antecedents=antecedents,
                consequent=(
                    consequent_variable,
                    consequent_term
                ),
                operator=fuzzy_operator,
                weight=peso,
                label=str(label_text) if label_text is not None else None
            )

            self.system.add_rule(
                nueva_regla
            )


    # =====================================================
    # VALIDACIÓN DE ESQUEMA JSON
    # =====================================================

    def _validar_metadata(self, datos, path):
        """!
        @brief Valida la estructura de metadata.json.

        @param datos Diccionario cargado del JSON.
        @param path Ruta del fichero (para mensajes de error).
        @raises ValueError Si falta algún campo obligatorio.
        """

        campos_obligatorios = [
            "autor",
            "version",
            "descripcion"
        ]

        for campo in campos_obligatorios:

            if campo not in datos:

                raise ValueError(
                    f"[Schema] '{path}': "
                    f"falta el campo obligatorio "
                    f"'{campo}' en metadata."
                )

    def _validar_variable(
        self,
        nombre,
        definicion,
        path
    ):
        """!
        @brief Valida la definición de una variable fuzzy.

        @details
        Comprueba:
            - Presencia de 'universo' o tipo 'categorica'
            - Presencia de 'terminos'
            - Para variables numéricas: universo con 3 elementos
            - Para cada término: 'funcion' y 'params' presentes
            - 'funcion' debe ser una de las soportadas

        @param nombre Nombre de la variable.
        @param definicion Diccionario de definición.
        @param path Ruta del fichero.
        @raises ValueError Si la definición es inválida.
        """

        tipo = definicion.get("tipo", "numerica")

        if tipo == "categorica":

            if "terminos" not in definicion:

                raise ValueError(
                    f"[Schema] '{path}': "
                    f"variable categorica '{nombre}' "
                    f"no tiene 'terminos'."
                )

            for t_nombre, t_valores in definicion[
                "terminos"
            ].items():

                if not isinstance(t_valores, list):

                    raise ValueError(
                        f"[Schema] '{path}': "
                        f"termino '{t_nombre}' de '{nombre}' "
                        f"debe ser una lista de valores."
                    )

            return

        # Variable numérica
        if "universo" not in definicion:

            raise ValueError(
                f"[Schema] '{path}': "
                f"variable '{nombre}' no tiene 'universo'."
            )

        universo = definicion["universo"]

        if (
            not isinstance(universo, list)
            or len(universo) != 3
        ):

            raise ValueError(
                f"[Schema] '{path}': "
                f"'universo' de '{nombre}' debe ser "
                f"[inicio, fin, paso] con 3 elementos. "
                f"Encontrado: {universo}"
            )

        if "terminos" not in definicion:

            raise ValueError(
                f"[Schema] '{path}': "
                f"variable '{nombre}' no tiene 'terminos'."
            )

        funciones_soportadas = set(
            self.FUNCIONES_FUZZY.keys()
        )

        for t_nombre, t_def in definicion[
            "terminos"
        ].items():

            if "funcion" not in t_def:

                raise ValueError(
                    f"[Schema] '{path}': "
                    f"termino '{t_nombre}' de '{nombre}' "
                    f"no tiene 'funcion'."
                )

            if t_def["funcion"] not in funciones_soportadas:

                raise ValueError(
                    f"[Schema] '{path}': "
                    f"termino '{t_nombre}' de '{nombre}' "
                    f"usa funcion desconocida "
                    f"'{t_def['funcion']}'. "
                    f"Soportadas: {funciones_soportadas}"
                )

            if "params" not in t_def:

                raise ValueError(
                    f"[Schema] '{path}': "
                    f"termino '{t_nombre}' de '{nombre}' "
                    f"no tiene 'params'."
                )

            if not isinstance(t_def["params"], list):

                raise ValueError(
                    f"[Schema] '{path}': "
                    f"'params' de '{t_nombre}' en "
                    f"'{nombre}' debe ser una lista."
                )

    def _validar_regla(self, regla, indice, path):
        """!
        @brief Valida la definición de una regla fuzzy.

        @details
        Comprueba:
            - Presencia de 'antecedentes' y 'consecuente'
            - Cada antecedente tiene 'variable' y 'termino'
            - El consecuente tiene 'variable' y 'termino'
            - 'peso' es un número positivo si está presente

        @param regla Diccionario de la regla.
        @param indice Índice de la regla (para mensajes).
        @param path Ruta del fichero.
        @raises ValueError Si la regla es inválida.
        """

        if "antecedentes" not in regla:

            raise ValueError(
                f"[Schema] '{path}': "
                f"regla #{indice} no tiene 'antecedentes'."
            )

        if not isinstance(regla["antecedentes"], list):

            raise ValueError(
                f"[Schema] '{path}': "
                f"'antecedentes' de regla #{indice} "
                f"debe ser una lista."
            )

        for i, ant in enumerate(
            regla["antecedentes"]
        ):

            for campo in ("variable", "termino"):

                if campo not in ant:

                    raise ValueError(
                        f"[Schema] '{path}': "
                        f"antecedente #{i} de regla "
                        f"#{indice} no tiene '{campo}'."
                    )

        if "consecuente" not in regla:

            raise ValueError(
                f"[Schema] '{path}': "
                f"regla #{indice} no tiene 'consecuente'."
            )

        for campo in ("variable", "termino"):

            if campo not in regla["consecuente"]:

                raise ValueError(
                    f"[Schema] '{path}': "
                    f"consecuente de regla #{indice} "
                    f"no tiene '{campo}'."
                )

        peso = regla.get("peso", 1.0)

        if not isinstance(peso, (int, float)):

            raise ValueError(
                f"[Schema] '{path}': "
                f"'peso' de regla #{indice} "
                f"debe ser un numero."
            )

        if peso < 0:

            raise ValueError(
                f"[Schema] '{path}': "
                f"'peso' de regla #{indice} "
                f"no puede ser negativo."
            )

    # =====================================================
    # VALIDACIÓN DE ENTRADAS
    # =====================================================

    def _validar_y_clipear_inputs(self, inputs):
        """!
        @brief Valida y recorta entradas fuera del universo.

        @details
        Para cada variable de entrada numérica comprueba
        que el valor esté dentro del universo declarado
        en la base de conocimiento.

        Si el valor está fuera del rango [u_min, u_max]:
            - Se recorta al límite más cercano.
            - Se emite un warnings.warn con detalle.

        Las variables categóricas (string) se omiten.

        @param inputs Diccionario de entradas sin validar.
        @return Diccionario de entradas validadas.
        """

        validados = {}

        for nombre, valor in inputs.items():

            # Variables categóricas: sin universo numérico
            if isinstance(valor, str):
                validados[nombre] = valor
                continue

            variable = self.variables.get(nombre)

            if variable is None:
                validados[nombre] = valor
                continue

            universe = variable.universe
            u_min = float(universe[0])
            u_max = float(universe[-1])

            if valor < u_min or valor > u_max:

                valor_recortado = float(
                    np.clip(valor, u_min, u_max)
                )

                warnings.warn(
                    f"[Clipping] '{nombre}' = {valor} "
                    f"fuera del universo [{u_min}, {u_max}]. "
                    f"Se recorta a {valor_recortado}.",
                    UserWarning,
                    stacklevel=2
                )

                validados[nombre] = valor_recortado

            else:

                validados[nombre] = valor

        return validados

    # =====================================================
    # PREDICCIÓN
    # =====================================================

    def predecir(self):
        """!
        @brief Ejecuta inferencia fuzzy.

        @return Resultado de inferencia.
        """

        inputs = {

            # DEMOGRÁFICOS
            "edad":
                self.moduloDemografico.obtener_edad(),

            "peso_relativo":
                self.moduloDemografico
                .obtener_peso_rel(),

            "raza":
                self.moduloDemografico.obtener_raza(),

            # CLÍNICOS
            "polidipsia":
                1.0 if self.moduloClinico
                .obtener_polidipsia()
                else 0.0,

            "abdomen":
                1.0 if self.moduloClinico
                .obtener_abdomen_inflamado()
                else 0.0,

            "alopecia":
                1.0 if self.moduloClinico
                .obtener_alopecia()
                else 0.0,

            "poliuria":
                1.0 if self.moduloClinico
                .obtener_poliuria()
                else 0.0,

            "polifagia":
                1.0 if self.moduloClinico
                .obtener_polifagia()
                else 0.0,

            "debilidad_muscular":
                1.0 if self.moduloClinico
                .obtener_debilidad_muscular()
                else 0.0,

            "piel_fina":
                1.0 if self.moduloClinico
                .obtener_piel_fina()
                else 0.0,

            "jadeo":
                1.0 if self.moduloClinico
                .obtener_jadeo()
                else 0.0,

            # LABORATORIO
            "alp":
                self.moduloLaboratorio
                .obtener_alp(),

            "alt":
                self.moduloLaboratorio
                .obtener_alt(),

            "usg":
                self.moduloLaboratorio
                .obtener_usg(),

            "colesterol":
                self.moduloLaboratorio
                .obtener_colesterol()
        }

        inputs = self._validar_y_clipear_inputs(
            inputs
        )

        results = self.system.infer(
            inputs,
            self.variables["riesgo"]
        )

        return results

    # =====================================================
    # EXPLICABILIDAD
    # =====================================================

    def explicar_decision(self):
        """!
        @brief Muestra reglas activadas.
        """

        inputs = {

            "edad":
                self.moduloDemografico.obtener_edad(),

            "peso_relativo":
                self.moduloDemografico
                .obtener_peso_rel(),

            "raza":
                self.moduloDemografico.obtener_raza(),

            "polidipsia":
                1.0 if self.moduloClinico
                .obtener_polidipsia()
                else 0.0,

            "abdomen":
                1.0 if self.moduloClinico
                .obtener_abdomen_inflamado()
                else 0.0,

            "alopecia":
                1.0 if self.moduloClinico
                .obtener_alopecia()
                else 0.0,

            "poliuria":
                1.0 if self.moduloClinico
                .obtener_poliuria()
                else 0.0,

            "polifagia":
                1.0 if self.moduloClinico
                .obtener_polifagia()
                else 0.0,

            "debilidad_muscular":
                1.0 if self.moduloClinico
                .obtener_debilidad_muscular()
                else 0.0,

            "piel_fina":
                1.0 if self.moduloClinico
                .obtener_piel_fina()
                else 0.0,

            "jadeo":
                1.0 if self.moduloClinico
                .obtener_jadeo()
                else 0.0,

            "alp":
                self.moduloLaboratorio
                .obtener_alp(),

            "alt":
                self.moduloLaboratorio
                .obtener_alt(),

            "usg":
                self.moduloLaboratorio
                .obtener_usg(),

            "colesterol":
                self.moduloLaboratorio
                .obtener_colesterol()
        }

        results = self.system.get_active_rules(
            inputs
        )

        print("\n" + "=" * 50)

        print(
            "INFORME DE EXPLICABILIDAD"
        )

        print("=" * 50)

        for result in results:

            print(
                f"ACTIVACIÓN: "
                f"{result.activation:.3f}"
            )

            print(
                f"CONSECUENTE: "
                f"{result.consequent}"
            )

            print(
                f"PESO: "
                f"{result.rule.weight}"
            )

            print("-" * 50)