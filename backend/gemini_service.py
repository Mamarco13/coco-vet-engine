"""!
@file gemini_service.py
@brief Servicio de extracción de datos clínicos de documentos usando la API de Gemini.

Recibe los bytes de un archivo (PDF, CSV o Excel) y retorna un JSON con los
campos del formulario de análisis de Cushing que haya podido identificar.
Los campos no encontrados se retornan como null.
"""

import json
import os
from typing import Optional

import google.generativeai as genai
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Carga las variables de entorno desde backend/.env (si existe)
load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# Esquema de datos estructurados que Gemini deberá respetar en su respuesta
# ─────────────────────────────────────────────────────────────────────────────

class ExtractedDocument(BaseModel):
    """Campos clínicos y de laboratorio para el análisis de Cushing canino."""

    # Demográficos
    edad: Optional[float] = Field(
        None,
        description="Edad del animal en años (ej: 8.5). Null si no se menciona."
    )
    raza: Optional[str] = Field(
        None,
        description="Raza del perro en texto libre (ej: 'Golden Retriever'). Null si no se menciona."
    )
    peso: Optional[float] = Field(
        None,
        description=(
            "Peso relativo del animal en porcentaje respecto a la media de su raza (ej: 120). "
            "Si el documento indica el peso en kg pero no el porcentaje, retorna null."
        )
    )

    # Laboratorio
    alp: Optional[float] = Field(
        None,
        description="Fosfatasa Alcalina (ALP/FA) en U/L. Null si no aparece."
    )
    alt: Optional[float] = Field(
        None,
        description="Alanina Aminotransferasa (ALT/GPT) en U/L. Null si no aparece."
    )
    usg: Optional[float] = Field(
        None,
        description="Gravedad Específica de la Orina (USG/densidad orina). Null si no aparece."
    )
    colesterol: Optional[float] = Field(
        None,
        description="Colesterol total en mg/dL. Null si no aparece."
    )

    # Signos clínicos (presencia = true, ausencia = false, no mencionado = null)
    polidipsia: Optional[bool] = Field(
        None,
        description="Polidipsia (bebe más agua de lo habitual). Null si no se menciona."
    )
    abdomen_inflamado: Optional[bool] = Field(
        None,
        description="Distensión o abdomen inflamado. Null si no se menciona."
    )
    alopecia: Optional[bool] = Field(
        None,
        description="Alopecia o pérdida de pelo. Null si no se menciona."
    )
    polifagia: Optional[bool] = Field(
        None,
        description="Polifagia (apetito excesivo). Null si no se menciona."
    )
    poliuria: Optional[bool] = Field(
        None,
        description="Poliuria (orina en mayor cantidad). Null si no se menciona."
    )
    debilidad: Optional[bool] = Field(
        None,
        description="Debilidad muscular o dificultad para moverse. Null si no se menciona."
    )
    piel_fina: Optional[bool] = Field(
        None,
        description="Piel fina, frágil o con hematomas. Null si no se menciona."
    )
    jadeo: Optional[bool] = Field(
        None,
        description="Jadeo constante sin esfuerzo aparente. Null si no se menciona."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Prompt principal
# ─────────────────────────────────────────────────────────────────────────────

EXTRACTION_PROMPT = """
Eres un asistente especializado en análisis de documentos veterinarios.
Tu tarea es extraer datos clínicos y de laboratorio de un documento (informe de analítica,
historia clínica o reporte veterinario) para el diagnóstico de Síndrome de Cushing en perros.

Instrucciones:
1. Lee el documento adjunto con atención, independientemente de su formato o diseño.
2. Extrae únicamente los valores que estén explícitamente presentes en el documento.
3. Si un campo NO aparece en el documento, devuelve null para ese campo. NO inventes valores.
4. Para los signos clínicos booleanos: true si se menciona como presente, false si se menciona
   explícitamente como ausente, null si no se menciona en absoluto.
5. Para los valores numéricos de laboratorio, usa las unidades especificadas en el esquema.
   Si el documento usa unidades distintas, conviértelas cuando sea posible; si no puedes
   convertir con seguridad, devuelve null.
6. Responde ÚNICAMENTE con el JSON estructurado, sin texto adicional.
"""


# ─────────────────────────────────────────────────────────────────────────────
# Función principal de extracción
# ─────────────────────────────────────────────────────────────────────────────

def extract_document_data(file_bytes: bytes, mime_type: str) -> str:
    """
    Envía un documento a Gemini y extrae los campos clínicos relevantes.

    Args:
        file_bytes: Contenido binario del archivo.
        mime_type:  Tipo MIME del archivo (ej: "application/pdf").

    Returns:
        String JSON con los campos extraídos (puede contener nulls).

    Raises:
        ValueError: Si la API key no está configurada.
        RuntimeError: Si la llamada a Gemini falla.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "La variable de entorno GEMINI_API_KEY no está configurada. "
            "Crea el archivo backend/.env con GEMINI_API_KEY=tu_clave."
        )

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=ExtractedDocument,
            temperature=0.0,   # máxima determinismo para extracción de datos
        ),
    )

    # Empaqueta el archivo como parte inline (sin subida previa a Files API)
    document_part = {
        "mime_type": mime_type,
        "data": file_bytes,
    }

    try:
        response = model.generate_content([document_part, EXTRACTION_PROMPT])
        return response.text
    except Exception as exc:
        raise RuntimeError(f"Error al llamar a la API de Gemini: {exc}") from exc


# ─────────────────────────────────────────────────────────────────────────────
# Helper: identificar campos null (usada por el endpoint de la API)
# ─────────────────────────────────────────────────────────────────────────────

def get_missing_fields(extracted_json: str) -> list[str]:
    """
    Dado el JSON devuelto por extract_document_data, retorna la lista de
    nombres de campos cuyo valor es null.
    """
    try:
        data = json.loads(extracted_json)
    except json.JSONDecodeError:
        return list(ExtractedDocument.model_fields.keys())

    return [field for field, value in data.items() if value is None]
