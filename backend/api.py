from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
import numpy as np

from backend.modulos.moduloDemografico import ModuloDemografico
from backend.modulos.moduloClinico import ModuloClinico
from backend.modulos.moduloLaboratorio import ModuloLaboratorio
from backend.sistema.prediccionCushing import PrediccionCushing

app = FastAPI(title="C.O.C.O API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        # GitHub Pages — cambia "Mamarco13" y "coco-vet-engine" si es necesario
        "https://mamarco13.github.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CushingInput(BaseModel):
    edad: float
    raza: str
    peso: float
    polidipsia: bool = False
    abdomen_inflamado: bool = False
    alopecia: bool = False
    polifagia: bool = False
    poliuria: bool = False
    debilidad: bool = False
    piel_fina: bool = False
    jadeo: bool = False
    alp: float
    alt: float
    usg: float
    colesterol: float


def serialize_result(result):
    rules = []
    for item in result.get("rules", []):
        rules.append({
            "activation": getattr(item, "activation", None),
            "consequent": getattr(item, "consequent", None),
            "weight": getattr(getattr(item, "rule", None), "weight", None),
            "label": getattr(getattr(item, "rule", None), "label", None),
        })

    return {
        "crisp": result.get("crisp"),
        "label": result.get("label"),
        "etiqueta": result.get("etiqueta"),
        "confidence": result.get("confidence"),
        "fuerza": result.get("fuerza"),
        "consenso": result.get("consenso"),
        "rules": rules,
        "aggregated": (
            result["aggregated"].tolist()
            if isinstance(result.get("aggregated"), np.ndarray)
            else result.get("aggregated")
        ),
    }


@app.post("/predict/cushing")
def predict_cushing(payload: CushingInput):
    modulo_demografico = ModuloDemografico(
        edad=payload.edad,
        raza=payload.raza,
        peso_rel=payload.peso,
    )

    modulo_clinico = ModuloClinico(
        polidipsia=payload.polidipsia,
        abdomen_inflamado=payload.abdomen_inflamado,
        alopecia=payload.alopecia,
        polifagia=payload.polifagia,
        poliuria=payload.poliuria,
        debilidad_muscular=payload.debilidad,
        piel_fina=payload.piel_fina,
        jadeo=payload.jadeo,
    )

    modulo_laboratorio = ModuloLaboratorio(
        alp=payload.alp,
        alt=payload.alt,
        usg=payload.usg,
        colesterol=payload.colesterol,
    )

    predictor = PrediccionCushing(
        moduloDemografico=modulo_demografico,
        moduloClinico=modulo_clinico,
        moduloLaboratorio=modulo_laboratorio,
    )

    predictor.fuzzificar_datos()
    predictor.implementar_reglas()

    result = predictor.predecir()
    return jsonable_encoder(serialize_result(result))