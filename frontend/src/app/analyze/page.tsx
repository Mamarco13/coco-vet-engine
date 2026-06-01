"use client";

import Image from "next/image";
import { ChangeEvent, useState } from "react";
import pataImg from "../../../public/pata.png";
import { useRouter } from "next/navigation";
import { analyzeCushing } from "@/lib/api";
import { diseases } from "@/lib/diseases";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DiseaseBadge } from "@/components/ui/DiseaseBadge";
import { Loader } from "@/components/ui/Loader";
import { Modal } from "@/components/ui/Modal";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { DocumentUploader } from "@/components/ui/DocumentUploader";
import { VoiceRecorder } from "@/components/ui/VoiceRecorder";
import type { ExtractedFormData } from "@/components/ui/DocumentUploader";

type CushingFormState = {
  edad: string;
  raza: string;
  peso: string;
  alp: string;
  alt: string;
  usg: string;
  colesterol: string;
  polidipsia: boolean;
  abdomen_inflamado: boolean;
  alopecia: boolean;
  polifagia: boolean;
  poliuria: boolean;
  debilidad: boolean;
  piel_fina: boolean;
  jadeo: boolean;
};

type ClinicalKey =
  | "polidipsia"
  | "abdomen_inflamado"
  | "alopecia"
  | "polifagia"
  | "poliuria"
  | "debilidad"
  | "piel_fina"
  | "jadeo";

const initialForm: CushingFormState = {
  edad: "",
  raza: "",
  peso: "",
  alp: "",
  alt: "",
  usg: "",
  colesterol: "",
  polidipsia: false,
  abdomen_inflamado: false,
  alopecia: false,
  polifagia: false,
  poliuria: false,
  debilidad: false,
  piel_fina: false,
  jadeo: false,
};

const CLINICAL_SIGNS: Array<{ key: ClinicalKey; label: string; desc: string }> = [
  { key: "polidipsia", label: "Polidipsia", desc: "Bebe más agua de lo habitual" },
  { key: "abdomen_inflamado", label: "Abdomen inflamado", desc: "Distensión abdominal visible" },
  { key: "alopecia", label: "Alopecia", desc: "Pérdida de pelo simétrica" },
  { key: "polifagia", label: "Polifagia", desc: "Apetito excesivo constante" },
  { key: "poliuria", label: "Poliuria", desc: "Orina en mayor cantidad" },
  { key: "debilidad", label: "Debilidad muscular", desc: "Dificultad para levantarse o moverse" },
  { key: "piel_fina", label: "Piel fina", desc: "Piel frágil o con hematomas" },
  { key: "jadeo", label: "Jadeo", desc: "Respiración jadeante sin esfuerzo" },
];

/* ─── Estilos reutilizables ──────────────────────────────────────────────── */
const inputCls =
  "w-full rounded-2xl border border-black/10 bg-white/80 px-4 py-2.5 text-sm text-[var(--foreground)] placeholder:text-[var(--muted)] focus:outline-none focus:ring-2 focus:ring-[var(--accent)]/40 transition";

const inputMissingCls =
  "w-full rounded-2xl border-2 border-amber-300 bg-amber-50/60 px-4 py-2.5 text-sm text-[var(--foreground)] placeholder:text-[var(--muted)] focus:outline-none focus:ring-2 focus:ring-amber-400/40 transition";

const labelCls = "block text-xs font-semibold uppercase tracking-[0.2em] text-[var(--muted)] mb-1.5";

const sectionHeadCls =
  "flex items-center gap-2 text-xs font-bold uppercase tracking-[0.25em] text-[var(--muted)]";

export default function AnalyzePage() {
  const router = useRouter();
  const [selectedDisease, setSelectedDisease] = useState(diseases[0].id);
  const [form, setForm] = useState<CushingFormState>(initialForm);
  const [error, setError] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [missingFields, setMissingFields] = useState<string[]>([]);

  /** Merges Gemini-extracted fields into the current form state */
  const handleDocumentExtracted = (data: ExtractedFormData, missing: string[]) => {
    setMissingFields(missing);
    setForm((prev) => {
      const next = { ...prev };
      for (const [key, value] of Object.entries(data)) {
        if (value === null || value === undefined) continue;
        if (key in prev) {
          // Los booleanos se mantienen; números/strings se convierten a strings para los inputs
          (next as Record<string, unknown>)[key] =
            typeof value === "boolean" ? value : String(value);
        }
      }
      return next;
    });
  };

  /** Returns the appropriate input CSS class, highlighting missing fields */
  const cls = (field: string) =>
    missingFields.includes(field) ? inputMissingCls : inputCls;

  const handleText = (key: keyof CushingFormState) => {
    return (event: ChangeEvent<HTMLInputElement>) => {
      setForm((prev) => ({ ...prev, [key]: event.target.value }));
    };
  };

  const handleCheck = (key: keyof CushingFormState) => {
    return (event: ChangeEvent<HTMLInputElement>) => {
      setForm((prev) => ({ ...prev, [key]: event.target.checked }));
    };
  };

  const parseNumber = (value: string) => {
    if (!value.trim()) return Number.NaN;
    return Number(value);
  };

  const startAnalysis = async () => {
    const payload = {
      edad: parseNumber(form.edad),
      raza: form.raza.trim(),
      peso: parseNumber(form.peso),
      polidipsia: form.polidipsia,
      abdomen_inflamado: form.abdomen_inflamado,
      alopecia: form.alopecia,
      polifagia: form.polifagia,
      poliuria: form.poliuria,
      debilidad: form.debilidad,
      piel_fina: form.piel_fina,
      jadeo: form.jadeo,
      alp: parseNumber(form.alp),
      alt: parseNumber(form.alt),
      usg: parseNumber(form.usg),
      colesterol: parseNumber(form.colesterol),
    };

    const requiredOk =
      payload.raza.length > 0 &&
      Number.isFinite(payload.edad) &&
      Number.isFinite(payload.peso) &&
      Number.isFinite(payload.alp) &&
      Number.isFinite(payload.alt) &&
      Number.isFinite(payload.usg) &&
      Number.isFinite(payload.colesterol);

    if (!requiredOk) {
      setError("Completa los campos obligatorios antes de continuar.");
      return;
    }

    setError(null);
    setIsAnalyzing(true);
    setProgress(8);

    const timer = window.setInterval(() => {
      setProgress((current) => (current < 90 ? current + Math.random() * 6 : current));
    }, 180);

    try {
      const result = await analyzeCushing({ diseaseId: selectedDisease, payload });
      window.sessionStorage.setItem("analysisResult", JSON.stringify(result));
      setProgress(100);
      router.push(`/results?d=${result.diseaseId}`);
    } catch {
      setError("No se pudo completar el análisis. Intenta nuevamente.");
    } finally {
      window.clearInterval(timer);
      setIsAnalyzing(false);
    }
  };

  /* Conteo de signos activos para feedback visual */
  const activeSignsCount = CLINICAL_SIGNS.filter((s) => form[s.key]).length;

  return (
    <div className="mx-auto w-full max-w-6xl px-6 pb-20 pt-6">
      <div className="flex flex-col gap-8 lg:flex-row lg:items-start">

        {/* ══════════════════════════════════════════════
            FORMULARIO PRINCIPAL
        ══════════════════════════════════════════════ */}
        <div className="flex-1 space-y-6">
          <div className="space-y-2">
            <DiseaseBadge label="Análisis" />
            <h1 className="font-display text-4xl font-semibold text-[var(--foreground)]">
              Análisis clínico
            </h1>
            <p className="max-w-xl text-sm text-[var(--muted)]">
              Completa los parámetros demográficos, clínicos y de laboratorio para estimar el riesgo
              con el motor difuso.
            </p>
          </div>

          <Card className="space-y-8">

            {/* ── Carga de documento con IA ── */}
            <div className="space-y-3">
              <p className={sectionHeadCls}>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" /></svg>
                Extracción automática con IA
              </p>
              <DocumentUploader onExtracted={handleDocumentExtracted} />

              {/* Divider voz/documento */}
              <div className="flex items-center gap-3 py-1">
                <div className="h-px flex-1 bg-black/6" />
                <p className="text-[10px] font-semibold uppercase tracking-[0.3em] text-[var(--muted)]">o dicta por voz</p>
                <div className="h-px flex-1 bg-black/6" />
              </div>

              <VoiceRecorder onExtracted={handleDocumentExtracted} />
            </div>

            {/* Divider */}
            <div className="flex items-center gap-3">
              <div className="h-px flex-1 bg-black/6" />
              <p className="text-[10px] font-semibold uppercase tracking-[0.3em] text-[var(--muted)]">o introduce los datos manualmente</p>
              <div className="h-px flex-1 bg-black/6" />
            </div>

            {/* ── Selector de enfermedad ── */}
            <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-black/5 bg-[var(--accent)]/5 px-5 py-4">
              <div>
                <p className={sectionHeadCls}>
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true"><circle cx="12" cy="12" r="10" /><path d="M12 8v4m0 4h.01" /></svg>
                  Enfermedad
                </p>
                <p className="mt-1 text-sm font-semibold text-[var(--foreground)]">Selección actual</p>
              </div>
              <select
                value={selectedDisease}
                onChange={(e) => setSelectedDisease(e.target.value)}
                className="rounded-full border border-black/10 bg-white/80 px-4 py-2 text-sm font-semibold text-[var(--foreground)] focus:outline-none focus:ring-2 focus:ring-[var(--accent)]/40"
              >
                {diseases.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name}
                  </option>
                ))}
              </select>
            </div>

            {/* ── Datos demográficos ── */}
            <div className="space-y-4">
              <p className={sectionHeadCls}>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" /></svg>
                Datos demográficos
              </p>
              <div className="grid gap-4 md:grid-cols-3">
                <div>
                  <label className={labelCls}>Edad (años) *</label>
                  <input
                    type="number"
                    min="0"
                    step="0.1"
                    value={form.edad}
                    onChange={handleText("edad")}
                    placeholder="Ej: 8"
                    className={cls("edad")}
                  />
                  <p className="mt-1 text-[11px] text-[var(--muted)]">Edad aproximada en años decimales</p>
                </div>
                <div>
                  <label className={labelCls}>Raza *</label>
                  <input
                    type="text"
                    value={form.raza}
                    onChange={handleText("raza")}
                    placeholder="Ej: Golden Retriever"
                    className={cls("raza")}
                  />
                  <p className="mt-1 text-[11px] text-[var(--muted)]">Raza del animal evaluado</p>
                </div>
                <div>
                  <label className={labelCls}>Peso relativo (%) *</label>
                  <input
                    type="number"
                    min="0"
                    step="1"
                    value={form.peso}
                    onChange={handleText("peso")}
                    placeholder="Ej: 120"
                    className={cls("peso")}
                  />
                  <p className="mt-1 text-[11px] text-[var(--muted)]">% respecto a la media de su raza</p>
                </div>
              </div>
            </div>

            {/* Divider */}
            <div className="h-px bg-black/6" />

            {/* ── Signos clínicos ── */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <p className={sectionHeadCls}>
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true"><path d="M22 12h-4l-3 9L9 3l-3 9H2" /></svg>
                  Signos clínicos
                </p>
                {activeSignsCount > 0 && (
                  <span
                    className="rounded-full px-2.5 py-0.5 text-[11px] font-semibold"
                    style={{ background: "rgba(13,139,141,0.12)", color: "var(--accent)" }}
                  >
                    {activeSignsCount} activo{activeSignsCount !== 1 ? "s" : ""}
                  </span>
                )}
              </div>
              <div className="grid gap-2.5 sm:grid-cols-2">
                {CLINICAL_SIGNS.map((item) => {
                  const checked = form[item.key];
                  return (
                    <label
                      key={item.key}
                      className="group flex cursor-pointer items-start gap-3 rounded-2xl border px-4 py-3 transition-all"
                      style={{
                        borderColor: checked ? "rgba(13,139,141,0.35)" : "rgba(0,0,0,0.08)",
                        background: checked
                          ? "linear-gradient(135deg, rgba(13,139,141,0.06) 0%, rgba(13,139,141,0.02) 100%)"
                          : "rgba(255,255,255,0.6)",
                      }}
                    >
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={handleCheck(item.key)}
                        className="mt-0.5 h-4 w-4 shrink-0 accent-[var(--accent)]"
                      />
                      <div>
                        <p
                          className="text-sm font-semibold leading-tight"
                          style={{ color: checked ? "var(--accent)" : "var(--foreground)" }}
                        >
                          {item.label}
                        </p>
                        <p className="mt-0.5 text-[11px] text-[var(--muted)]">{item.desc}</p>
                      </div>
                    </label>
                  );
                })}
              </div>
            </div>

            {/* Divider */}
            <div className="h-px bg-black/6" />

            {/* ── Laboratorio ── */}
            <div className="space-y-4">
              <p className={sectionHeadCls}>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true"><path d="M9 3H5a2 2 0 0 0-2 2v4m6-6h10a2 2 0 0 1 2 2v4M9 3v18m0 0h10a2 2 0 0 0 2-2v-4M9 21H5a2 2 0 0 1-2-2v-4m0 0h18" /></svg>
                Laboratorio
              </p>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className={labelCls}>ALP — Fosfatasa Alcalina (U/L) *</label>
                  <input
                    type="number"
                    min="0"
                    step="1"
                    value={form.alp}
                    onChange={handleText("alp")}
                    placeholder="Ej: 350"
                    className={cls("alp")}
                  />
                </div>
                <div>
                  <label className={labelCls}>ALT — Alanina Aminotransferasa (U/L) *</label>
                  <input
                    type="number"
                    min="0"
                    step="1"
                    value={form.alt}
                    onChange={handleText("alt")}
                    placeholder="Ej: 80"
                    className={cls("alt")}
                  />
                </div>
                <div>
                  <label className={labelCls}>USG — Gravedad Específica Orina *</label>
                  <input
                    type="number"
                    min="0"
                    step="0.001"
                    value={form.usg}
                    onChange={handleText("usg")}
                    placeholder="Ej: 1.008"
                    className={cls("usg")}
                  />
                </div>
                <div>
                  <label className={labelCls}>Colesterol (mg/dL) *</label>
                  <input
                    type="number"
                    min="0"
                    step="1"
                    value={form.colesterol}
                    onChange={handleText("colesterol")}
                    placeholder="Ej: 320"
                    className={cls("colesterol")}
                  />
                </div>
              </div>
            </div>

            {/* Error */}
            {error && (
              <div className="flex items-center gap-2.5 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#e11d48" strokeWidth="2" aria-hidden="true"><circle cx="12" cy="12" r="10" /><path d="M12 8v4m0 4h.01" /></svg>
                <p className="text-sm font-medium text-rose-700" role="alert">
                  {error}
                </p>
              </div>
            )}
          </Card>
        </div>

        {/* ══════════════════════════════════════════════
            SIDEBAR DERECHO
        ══════════════════════════════════════════════ */}
        <div className="w-full max-w-sm space-y-4">

          {/* Botón de acción principal */}
          <Card className="space-y-4">
            <div>
              <h3 className="text-base font-semibold text-[var(--foreground)]">
                Listo para analizar
              </h3>
              <p className="mt-1 text-xs text-[var(--muted)]">
                Revisa que todos los campos obligatorios (*) estén completos.
              </p>
            </div>

            <ul className="space-y-2 text-sm text-[var(--muted)]">
              {[
                { ok: form.edad !== "" && form.raza !== "" && form.peso !== "", label: "Datos demográficos" },
                { ok: form.alp !== "" && form.alt !== "" && form.usg !== "" && form.colesterol !== "", label: "Laboratorio" },
                { ok: true, label: `${activeSignsCount} signo${activeSignsCount !== 1 ? "s" : ""} clínico${activeSignsCount !== 1 ? "s" : ""} registrado${activeSignsCount !== 1 ? "s" : ""}` },
              ].map((item) => (
                <li key={item.label} className="flex items-center gap-2.5">
                  <span
                    className="h-4 w-4 shrink-0 rounded-full text-center text-[10px] font-bold leading-4"
                    style={{
                      background: item.ok ? "rgba(13,139,141,0.15)" : "rgba(0,0,0,0.08)",
                      color: item.ok ? "var(--accent)" : "var(--muted)",
                    }}
                  >
                    {item.ok ? "✓" : "·"}
                  </span>
                  {item.label}
                </li>
              ))}
            </ul>

            <Button size="lg" onClick={startAnalysis} isLoading={isAnalyzing} disabled={isAnalyzing} className="w-full">
              Analizar ahora
            </Button>
            <p className="text-[11px] text-[var(--muted)]">
              Esta herramienta no sustituye la evaluación de un veterinario.
            </p>
          </Card>
        </div>
      </div>

      {/* Modal de progreso */}
      <Modal open={isAnalyzing} onClose={() => { }} dismissible={false} title="Analizando…">
        <div className="space-y-4">
          <Loader label="Procesando parámetros" />
          <ProgressBar value={progress} max={100} />
          <p className="text-sm text-[var(--muted)]">
            Estamos evaluando criterios clínicos y de laboratorio con el motor difuso. Esto suele
            tardar menos de 2 segundos.
          </p>
        </div>
      </Modal>
    </div>
  );
}
