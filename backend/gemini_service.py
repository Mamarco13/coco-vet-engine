"""!
@file gemini_service.py
@brief Servicio de extracción de datos clínicos usando la API de Gemini.

Soporta dos modos de entrada:
  - Documento (PDF, CSV, Excel): extract_document_data(file_bytes, mime_type)
  - Texto dictado por voz:       extract_voice_data(transcript)

Ambas funciones devuelven un JSON con los campos del formulario de análisis
de Cushing que hayan podido identificar. Los campos no encontrados se retornan
como null.
"""

import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Carga las variables de entorno desde backend/.env (si existe)
load_dotenv()

# Esquema de datos estructurados que Gemini deberá respetar en su respuesta

class ExtractedDocument(BaseModel):
    """Campos clínicos y de laboratorio para el análisis de Cushing canino."""

    # Demográficos
    edad: float | None = Field(
        description="Edad del animal en años (ej: 8.5). Null si no se menciona."
    )
    raza: str | None = Field(
        description="Raza del perro en texto libre (ej: 'Golden Retriever'). Null si no se menciona."
    )
    peso: float | None = Field(
        description=(
            "Peso relativo del animal en porcentaje respecto a la media de su raza (ej: 120). "
            "Si el documento indica el peso en kg pero no el porcentaje, retorna null."
        )
    )

    # Laboratorio
    alp: float | None = Field(
        description="Fosfatasa Alcalina (ALP/FA) en U/L. Null si no aparece."
    )
    alt: float | None = Field(
        description="Alanina Aminotransferasa (ALT/GPT) en U/L. Null si no aparece."
    )
    usg: float | None = Field(
        description="Gravedad Específica de la Orina (USG/densidad orina). Null si no aparece."
    )
    colesterol: float | None = Field(
        description="Colesterol total en mg/dL. Null si no aparece."
    )

    # Signos clínicos (presencia = true, ausencia = false, no mencionado = null)
    polidipsia: bool | None = Field(
        description="Polidipsia (bebe más agua de lo habitual). Null si no se menciona."
    )
    abdomen_inflamado: bool | None = Field(
        description="Distensión o abdomen inflamado. Null si no se menciona."
    )
    alopecia: bool | None = Field(
        description="Alopecia o pérdida de pelo. Null si no se menciona."
    )
    polifagia: bool | None = Field(
        description="Polifagia (apetito excesivo). Null si no se menciona."
    )
    poliuria: bool | None = Field(
        description="Poliuria (orina en mayor cantidad). Null si no se menciona."
    )
    debilidad: bool | None = Field(
        description="Debilidad muscular o dificultad para moverse. Null si no se menciona."
    )
    piel_fina: bool | None = Field(
        description="Piel fina, frágil o con hematomas. Null si no se menciona."
    )
    jadeo: bool | None = Field(
        description="Jadeo constante sin esfuerzo aparente. Null si no se menciona."
    )


# Prompt principal

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


# Función principal de extracción

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
        model_name="gemini-2.5-flash",
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=ExtractedDocument,
            temperature=0.0,   # máxima determinismo para extracción de datos
        ),
    )

    # Empaqueta el archivo como parte inline
    document_part = {
        "mime_type": mime_type,
        "data": file_bytes,
    }

    try:
        response = model.generate_content([document_part, EXTRACTION_PROMPT])
        return response.text
    except Exception as exc:
        raise RuntimeError(f"Error al llamar a la API de Gemini: {exc}") from exc


# Prompt para transcripciones de voz

VOICE_PROMPT = """
Eres un asistente especializado en veterinaria clínica canina.
Vas a recibir la transcripción literal de lo que ha dictado un veterinario
por micrófono sobre un paciente perro, posiblemente con lenguaje coloquial,
frases incompletas o términos no técnicos.

Tu tarea es interpretar esa transcripción y extraer los datos clínicos y
de laboratorio para el diagnóstico de Síndrome de Cushing en perros.

GUÍA DE INTERPRETACIÓN CLÍNICA (expresiones coloquiales → campo):

  Demográficos:
  - "tiene X años" / "es un perro de X años" / "paciente de X años"   → edad (número)
  - "raza X" / "es un X" / "Golden" / "Beagle" / etc.                 → raza (texto)
  - "pesa X kilos" / "X kg" (peso en kg) → retorna null para 'peso'
    (el campo 'peso' es el % relativo a la media de la raza, NO kg directos;
     solo rellénalo si el veterinario dice explícitamente un porcentaje
     como "pesa un 20% más" o "peso relativo 120%")

  Laboratorio (valores numéricos con sus unidades):
  - "ALP X" / "fosfatasa alcalina X" / "FA X"                         → alp (U/L)
  - "ALT X" / "GPT X" / "transaminasa X"                              → alt (U/L)
  - "densidad de orina X" / "USG X" / "gravedad específica X"         → usg
  - "colesterol X" / "col X mg/dL"                                    → colesterol

  Signos clínicos booleanos — marca TRUE si el veterinario indica presencia:
  - polidipsia:        "bebe mucho" / "bebe más de lo normal" / "mucha sed" /
                       "polidipsia" / "bebedor compulsivo" / "siempre en el
                       bebedero" / "consumo de agua aumentado"
  - abdomen_inflamado: "abdomen distendido" / "barriga hinchada" /
                       "vientre grande" / "distensión abdominal" /
                       "panza caída" / "barrigón"
  - alopecia:          "pérdida de pelo" / "se le cae el pelo" / "alopecia" /
                       "pelaje ralo" / "zonas sin pelo" / "calvicie" /
                       "pelaje deteriorado" / "no tiene pelo en el lomo"
  - polifagia:         "come mucho" / "apetito aumentado" / "siempre tiene
                       hambre" / "hambre voraz" / "polifagia" / "glotón" /
                       "no para de comer"
  - poliuria:          "orina mucho" / "hace pis muy seguido" / "muchas
                       micciones" / "poliuria" / "orina frecuente" /
                       "siempre quiere salir a orinar"
  - debilidad:         "le cuesta levantarse" / "débil" / "cansado" /
                       "debilidad muscular" / "no puede subir escaleras" /
                       "se cansa enseguida" / "atrofia muscular"
  - piel_fina:         "piel fina" / "piel frágil" / "hematomas fáciles" /
                       "piel arrugada" / "heridas que no cicatrizan" /
                       "piodermia" / "piel delicada"
  - jadeo:             "jadea" / "jadeante" / "respira con la boca abierta" /
                       "respiración agitada sin esfuerzo" / "pantea" /
                       "siempre agitado" / "jadeo persistente"

  Marca FALSE si el veterinario dice explícitamente que NO tiene ese signo
  ("no tiene polidipsia", "el pelo está bien", etc.).
  Si no se menciona en absoluto → null.

Instrucciones:
1. Interpreta el lenguaje coloquial con la guía anterior.
2. Extrae solo los valores mencionados. NO inventes datos.
3. Para signos clínicos: true = presente, false = ausente explícito, null = no mencionado.
4. Responde ÚNICAMENTE con el JSON estructurado, sin texto adicional.
"""


def extract_voice_data(transcript: str) -> str:
    """
    Interpreta la transcripción de voz de un veterinario y extrae los campos
    clínicos relevantes usando Gemini.

    Args:
        transcript: Texto transcrito del dictado de voz del veterinario.

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
        model_name="gemini-2.5-flash",
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=ExtractedDocument,
            temperature=0.0,
        ),
    )

    full_prompt = (
        f"{VOICE_PROMPT}\n\n"
        f"TRANSCRIPCIÓN DEL VETERINARIO:\n{transcript.strip()}"
    )

    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as exc:
        raise RuntimeError(f"Error al llamar a la API de Gemini: {exc}") from exc


# Identificar campos null

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
