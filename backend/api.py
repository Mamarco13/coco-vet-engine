import json

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import numpy as np

from modulos.moduloDemografico import ModuloDemografico
from modulos.moduloClinico import ModuloClinico
from modulos.moduloLaboratorio import ModuloLaboratorio
from sistema.prediccionCushing import PrediccionCushing
from gemini_service import extract_document_data, extract_voice_data, get_missing_fields


load_dotenv()

app = FastAPI(title="C.O.C.O API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
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


# ─── Tipos MIME permitidos para la extracción de documentos ───────────────────
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "text/csv",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
    "application/vnd.ms-excel",  # .xls
}


@app.post("/api/extraer-documento")
async def extraer_documento(file: UploadFile = File(...)):
    """
    Recibe un documento (PDF, CSV o Excel), lo envía a Gemini y retorna
    los campos clínicos extraídos junto con la lista de campos no encontrados.
    """
    # Validación de tipo de archivo
    content_type = file.content_type or ""
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Tipo de archivo no permitido: '{content_type}'. "
                "Solo se aceptan PDF, CSV o Excel (.xlsx / .xls)."
            ),
        )

    # Lectura del contenido binario
    file_bytes = await file.read()

    # Llamada al servicio de Gemini
    try:
        raw_json = extract_document_data(file_bytes, content_type)
    except ValueError as exc:
        # API key no configurada
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RuntimeError as exc:
        # Error de la API de Gemini
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    # Parsear el JSON devuelto por Gemini
    try:
        extracted_data = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=502,
            detail="La IA devolvió una respuesta con formato inválido.",
        ) from exc

    # Identificar campos que Gemini no pudo extraer (valor null)
    missing_fields = get_missing_fields(raw_json)

    return {
        "ok": True,
        "data": extracted_data,
        "missing_fields": missing_fields,
        "extracted_count": len(extracted_data) - len(missing_fields),
        "total_fields": len(extracted_data),
    }


class VoiceInput(BaseModel):
    """Transcripción de voz dictada por el veterinario."""
    transcript: str


@app.post("/api/extraer-voz")
async def extraer_voz(body: VoiceInput):
    """
    Recibe la transcripción de un dictado de voz del veterinario, la envía
    a Gemini y retorna los campos clínicos inferidos junto con los campos
    no encontrados. Devuelve la misma estructura que /api/extraer-documento.
    """
    if not body.transcript.strip():
        raise HTTPException(
            status_code=400,
            detail="El campo 'transcript' no puede estar vacío.",
        )

    try:
        raw_json = extract_voice_data(body.transcript)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    try:
        extracted_data = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=502,
            detail="La IA devolvió una respuesta con formato inválido.",
        ) from exc

    missing_fields = get_missing_fields(raw_json)

    return {
        "ok": True,
        "data": extracted_data,
        "missing_fields": missing_fields,
        "extracted_count": len(extracted_data) - len(missing_fields),
        "total_fields": len(extracted_data),
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