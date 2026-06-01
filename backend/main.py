"""!
@file main.py
@brief Ejemplo de ejecución del sistema fuzzy de predicción por línea de comandos.
"""

import argparse
from sistema.prediccionCushing import PrediccionCushing
from modulos.moduloDemografico import ModuloDemografico
from modulos.moduloClinico import ModuloClinico
from modulos.moduloLaboratorio import ModuloLaboratorio

def main():
    # CONFIGURACIÓN DE ARGUMENTOS DE TERMINAL
    parser = argparse.ArgumentParser(description="Motor C.O.C.O: Predicción de Cushing Canino")

    # -- Demográficos
    parser.add_argument("--edad", type=float, required=True, help="Edad del perro en años")
    parser.add_argument("--raza", type=str, required=True, help="Raza del perro (ej: bichon_frise)")
    parser.add_argument("--peso", type=float, required=True, help="Peso relativo (%%)")

    # -- Clínicos 
    parser.add_argument("--polidipsia", action="store_true", help="Presencia de polidipsia")
    parser.add_argument("--abdomen-inflamado", action="store_true", help="Presencia de abdomen inflamado")
    parser.add_argument("--alopecia", action="store_true", help="Presencia de alopecia")
    parser.add_argument("--polifagia", action="store_true", help="Presencia de polifagia")
    parser.add_argument("--poliuria", action="store_true", help="Presencia de poliuria")
    parser.add_argument("--debilidad", action="store_true", help="Presencia de debilidad muscular")
    parser.add_argument("--piel-fina", action="store_true", help="Presencia de piel fina")
    parser.add_argument("--jadeo", action="store_true", help="Presencia de jadeo constante")

    # -- Laboratorio
    parser.add_argument("--alp", type=float, required=True, help="Valor de Fosfatasa Alcalina (ALP)")
    parser.add_argument("--alt", type=float, required=True, help="Valor de Alanina Aminotransferasa (ALT)")
    parser.add_argument("--usg", type=float, required=True, help="Gravedad Específica de la Orina (USG)")
    parser.add_argument("--colesterol", type=float, required=True, help="Nivel de colesterol")

    # Parseamos los argumentos introducidos por el usuario
    args = parser.parse_args()

    # DATOS DEMOGRÁFICOS
    modulo_demografico = ModuloDemografico(
        edad=args.edad,
        raza=args.raza,
        peso_rel=args.peso
    )

    # DATOS CLÍNICOS
    modulo_clinico = ModuloClinico(
        polidipsia=args.polidipsia,
        abdomen_inflamado=args.abdomen_inflamado,
        alopecia=args.alopecia,
        polifagia=args.polifagia,
        poliuria=args.poliuria,
        debilidad_muscular=args.debilidad,
        piel_fina=args.piel_fina,
        jadeo=args.jadeo
    )

    # DATOS LABORATORIO
    modulo_laboratorio = ModuloLaboratorio(
        alp=args.alp,
        alt=args.alt,
        usg=args.usg,
        colesterol=args.colesterol
    )

    # CREACIÓN DEL SISTEMA Y EJECUCIÓN
    predictor = PrediccionCushing(
        moduloDemografico=modulo_demografico,
        moduloClinico=modulo_clinico,
        moduloLaboratorio=modulo_laboratorio
    )

    print("\nInicializando sistema fuzzy...")
    predictor.fuzzificar_datos()
    predictor.implementar_reglas()
    print("Sistema fuzzy inicializado correctamente.")

    print("\nEjecutando inferencia fuzzy...\n")
    resultados = predictor.predecir()

    # RESULTADOS
    print("\n")
    print("=" * 60)
    print("RESULTADO FINAL")
    print("=" * 60)
    print(f"Riesgo estimado: {resultados['crisp']:.3f}")
    print(f"Nivel de riesgo:  {resultados['etiqueta']}")
    print(f"Confianza fuzzy: {resultados['confidence']:.3f}")
    print(f"  · Fuerza:   {resultados['fuerza']:.3f}")
    print(f"  · Consenso: {resultados['consenso']:.3f}")
    print("=" * 60)
    
    print("REGLAS ACTIVADAS")
    print("=" * 60)

    if not resultados["rules"]:
        print("No se activó ninguna regla.")
    else:
        for indice, resultado in enumerate(resultados["rules"], start=1):
            print(f"\nRegla #{indice}")
            print(f"Activación: {resultado.activation:.3f}")
            print(f"Consecuente: {resultado.consequent}")
            print(f"Peso regla: {resultado.rule.weight}")
            print("-" * 40)

    print("\n")
    predictor.explicar_decision()
    print("\nFin de ejecución.")

if __name__ == "__main__":
    main()