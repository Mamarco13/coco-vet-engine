"""!
@file main.py
@brief Ejemplo de ejecución del sistema fuzzy de predicción.

@details
Este archivo muestra un ejemplo completo de uso
del sistema de predicción difusa para síndrome
de Cushing utilizando la base de conocimiento JSON.
"""

from sistema.prediccionCushing import PrediccionCushing

from modulos.moduloDemografico import ModuloDemografico
from modulos.moduloClinico import ModuloClinico
from modulos.moduloLaboratorio import ModuloLaboratorio


def main():

    # =====================================================
    # DATOS DEMOGRÁFICOS
    # =====================================================

    modulo_demografico = ModuloDemografico(
        edad=11,
        raza="bichon_frise",
        peso_rel=125
    )

    # =====================================================
    # DATOS CLÍNICOS
    # =====================================================

    modulo_clinico = ModuloClinico(
        polidipsia=True,
        abdomen_inflamado=True,
        alopecia=True,
        polifagia=True,
        poliuria=True,
        debilidad_muscular=True,
        piel_fina=False,
        jadeo=True
    )

    # =====================================================
    # DATOS LABORATORIO
    # =====================================================

    modulo_laboratorio = ModuloLaboratorio(
        alp=780,
        alt=220,
        usg=1.012,
        colesterol=410
    )

    # =====================================================
    # CREACIÓN DEL SISTEMA
    # =====================================================

    predictor = PrediccionCushing(
        moduloDemografico=modulo_demografico,
        moduloClinico=modulo_clinico,
        moduloLaboratorio=modulo_laboratorio
    )

    # =====================================================
    # CONSTRUCCIÓN DEL SISTEMA FUZZY
    # =====================================================

    print("\nInicializando sistema fuzzy...")

    predictor.fuzzificar_datos()

    predictor.implementar_reglas()

    print("Sistema fuzzy inicializado correctamente.")

    # =====================================================
    # EJECUCIÓN
    # =====================================================

    print("\nEjecutando inferencia fuzzy...\n")

    resultados = predictor.predecir()

    # =====================================================
    # RESULTADOS
    # =====================================================
    print("\n")

    print("=" * 60)
    print("RESULTADO FINAL")
    print("=" * 60)

    print(
        f"Riesgo estimado: "
        f"{resultados['crisp']:.3f}"
    )

    print(
        f"Nivel de riesgo:  "
        f"{resultados['etiqueta']}"
    )

    print(
        f"Confianza fuzzy: "
        f"{resultados['confidence']:.3f}"
    )

    print(
        f"  · Fuerza:   "
        f"{resultados['fuerza']:.3f}"
    )

    print(
        f"  · Consenso: "
        f"{resultados['consenso']:.3f}"
    )
    print("=" * 60)

    print("REGLAS ACTIVADAS")

    print("=" * 60)

    if not resultados["rules"]:

        print(
            "No se activó ninguna regla."
        )

    else:

        for indice, resultado in enumerate(
            resultados["rules"],
            start=1
        ):

            print(f"\nRegla #{indice}")

            print(
                f"Activación: "
                f"{resultado.activation:.3f}"
            )

            print(
                f"Consecuente: "
                f"{resultado.consequent}"
            )

            print(
                f"Peso regla: "
                f"{resultado.rule.weight}"
            )

            print("-" * 40)

    # =====================================================
    # EXPLICABILIDAD
    # =====================================================

    print("\n")

    predictor.explicar_decision()

    print("\nFin de ejecución.")


if __name__ == "__main__":

    main()