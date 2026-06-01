import { clamp01 } from "./format";
import { getDiseaseById } from "./diseases";

export type AnalysisResult = {
  diseaseId: string;
  score: number;
  label: string;
  confidence: number;
  summary: string;
  recommendations: string[];
  rules: Array<{ activation: number; consequent: string | string[]; weight: number; label?: string }>;
};

type CushingPayload = {
  edad: number;
  raza: string;
  peso: number;
  polidipsia?: boolean;
  abdomen_inflamado?: boolean;
  alopecia?: boolean;
  polifagia?: boolean;
  poliuria?: boolean;
  debilidad?: boolean;
  piel_fina?: boolean;
  jadeo?: boolean;
  alp: number;
  alt: number;
  usg: number;
  colesterol: number;
};

type CushingApiResponse = {
  crisp: number;
  label?: string;
  etiqueta?: string;
  confidence?: number;
  fuerza?: number;
  consenso?: number;
  rules?: Array<{ activation: number; consequent: string; weight: number }>;
  aggregated?: number[];
};

const RISK_LABELS = [
  { max: 0.2, label: "Muy bajo" },
  { max: 0.4, label: "Bajo" },
  { max: 0.6, label: "Medio" },
  { max: 0.8, label: "Alto" },
  { max: 1, label: "Muy alto" },
];

const RECOMMENDATIONS = [
  "Agenda una consulta veterinaria si notas cambios persistentes.",
  "Comparte el historial clinico y alimentacion actual.",
  "Monitorea apetito, sed y actividad durante la semana.",
];

function labelFromScore(score: number) {
  const entry = RISK_LABELS.find((item) => score <= item.max);
  return entry ? entry.label : "Medio";
}

function buildResult(diseaseId: string, score: number): AnalysisResult {
  const normalizedScore = clamp01(score);
  const disease = getDiseaseById(diseaseId);
  const label = labelFromScore(normalizedScore);
  const confidence = clamp01(0.62 + Math.random() * 0.25);

  return {
    diseaseId,
    score: normalizedScore,
    label,
    confidence,
    summary: `Resultado orientativo para ${disease.shortName}. No reemplaza una evaluacion clinica.`,
    recommendations: RECOMMENDATIONS,
    rules: [],
  };
}

function buildResultFromApi(
  diseaseId: string,
  data: CushingApiResponse
): AnalysisResult {
  const normalizedScore = clamp01(data.crisp ?? 0);
  const disease = getDiseaseById(diseaseId);
  const label = data.etiqueta ?? labelFromScore(normalizedScore);
  const confidence = clamp01(data.confidence ?? 0);

  return {
    diseaseId,
    score: normalizedScore,
    label,
    confidence,
    summary: `Resultado orientativo para ${disease.shortName}. No reemplaza una evaluacion clinica.`,
    recommendations: RECOMMENDATIONS,
    rules: (data.rules ?? []).map((rule) => ({
      activation: rule.activation,
      consequent: rule.consequent,
      weight: rule.weight,
      label: (rule as any).label,
    })),
  };
}

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

export async function analyzeCushing(params: {
  diseaseId: string;
  payload: CushingPayload;
}): Promise<AnalysisResult> {
  const response = await fetch(`${API_BASE}/predict/cushing`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params.payload),
  });

  if (!response.ok) {
    throw new Error("API error");
  }

  const data = (await response.json()) as CushingApiResponse;
  return buildResultFromApi(params.diseaseId, data);
}

export function buildMockResult(diseaseId: string) {
  return buildResult(diseaseId, 0.56);
}

// ─── Document Extraction ──────────────────────────────────────────────────────

export type ExtractionResult = {
  ok: boolean;
  /** Partial form fields extracted from the document (null values omitted). */
  data: Partial<Record<string, string | number | boolean | null>>;
  /** List of field names Gemini could not find in the document. */
  missing_fields: string[];
  extracted_count: number;
  total_fields: number;
};

/**
 * Uploads a document file to the backend and returns the fields
 * that Gemini was able to extract from it.
 */
export async function extractDocumentData(file: File): Promise<ExtractionResult> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/api/extraer-documento`, {
    method: "POST",
    body: formData,
    // Do NOT set Content-Type manually — the browser adds the correct
    // multipart/form-data boundary automatically.
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    const detail = errorBody?.detail ?? `Error ${response.status}`;
    throw new Error(detail);
  }

  return response.json() as Promise<ExtractionResult>;
}
