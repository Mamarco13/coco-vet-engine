"use client";

import { ChangeEvent, DragEvent, useRef, useState } from "react";
import { extractDocumentData, ExtractionResult } from "@/lib/api";

// ─── Iconos inline ────────────────────────────────────────────────────────────

const IconUpload = () => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="17 8 12 3 7 8" />
    <line x1="12" y1="3" x2="12" y2="15" />
  </svg>
);

const IconFile = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
    <polyline points="14 2 14 8 20 8" />
  </svg>
);

const IconCheck = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <polyline points="20 6 9 17 4 12" />
  </svg>
);

const IconWarning = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
    <line x1="12" y1="9" x2="12" y2="13" />
    <line x1="12" y1="17" x2="12.01" y2="17" />
  </svg>
);

const IconClose = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <line x1="18" y1="6" x2="6" y2="18" />
    <line x1="6" y1="6" x2="18" y2="18" />
  </svg>
);

// ─── Etiquetas legibles de los campos ─────────────────────────────────────────

const FIELD_LABELS: Record<string, string> = {
  edad: "Edad",
  raza: "Raza",
  peso: "Peso relativo (%)",
  alp: "ALP (Fosfatasa Alcalina)",
  alt: "ALT (Alanina Aminotransferasa)",
  usg: "USG (Gravedad Específica Orina)",
  colesterol: "Colesterol",
  polidipsia: "Polidipsia",
  abdomen_inflamado: "Abdomen inflamado",
  alopecia: "Alopecia",
  polifagia: "Polifagia",
  poliuria: "Poliuria",
  debilidad: "Debilidad muscular",
  piel_fina: "Piel fina",
  jadeo: "Jadeo",
};

// ─── Tipos ────────────────────────────────────────────────────────────────────

export type ExtractedFormData = Partial<Record<string, string | number | boolean | null>>;

type Props = {
  /** Callback fired when extraction succeeds. Receives the extracted fields (nulls excluded). */
  onExtracted: (data: ExtractedFormData, missingFields: string[]) => void;
};

type UploadState = "idle" | "selected" | "loading" | "success" | "error";

// ─── Componente ───────────────────────────────────────────────────────────────

export function DocumentUploader({ onExtracted }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [state, setState] = useState<UploadState>("idle");
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [result, setResult] = useState<ExtractionResult | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // ── File selection ──────────────────────────────────────────────────────────

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    selectFile(file);
  }

  function handleDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (!file) return;
    selectFile(file);
  }

  function selectFile(file: File) {
    // Reset previous results
    setResult(null);
    setErrorMsg(null);
    setSelectedFile(file);
    setState("selected");
  }

  function handleReset() {
    setSelectedFile(null);
    setResult(null);
    setErrorMsg(null);
    setState("idle");
    if (inputRef.current) inputRef.current.value = "";
  }

  // ── Upload & extraction ─────────────────────────────────────────────────────

  async function handleExtract() {
    if (!selectedFile) return;

    setState("loading");
    setErrorMsg(null);

    try {
      const data = await extractDocumentData(selectedFile);
      setResult(data);
      setState("success");
      // Pass only non-null values to parent
      const cleanData: ExtractedFormData = {};
      for (const [key, val] of Object.entries(data.data)) {
        if (val !== null && val !== undefined) cleanData[key] = val;
      }
      onExtracted(cleanData, data.missing_fields);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Error desconocido.");
      setState("error");
    }
  }

  // ── Render helpers ──────────────────────────────────────────────────────────

  const isLoading = state === "loading";
  const hasFile = selectedFile !== null;

  function fileIcon(name: string) {
    const ext = name.split(".").pop()?.toLowerCase();
    const colors: Record<string, string> = {
      pdf: "#e11d48",
      csv: "#16a34a",
      xlsx: "#2563eb",
      xls: "#2563eb",
    };
    return colors[ext ?? ""] ?? "var(--accent)";
  }

  return (
    <div className="space-y-3">
      {/* ── Drop zone ── */}
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        onClick={() => !hasFile && inputRef.current?.click()}
        role="button"
        aria-label="Zona de carga de documento"
        className="relative overflow-hidden rounded-2xl border-2 transition-all duration-200"
        style={{
          borderColor: isDragOver
            ? "var(--accent)"
            : hasFile
              ? "rgba(13,139,141,0.35)"
              : "rgba(0,0,0,0.1)",
          background: isDragOver
            ? "rgba(13,139,141,0.05)"
            : hasFile
              ? "linear-gradient(135deg, rgba(13,139,141,0.04) 0%, rgba(13,139,141,0.01) 100%)"
              : "rgba(255,255,255,0.7)",
          cursor: hasFile ? "default" : "pointer",
          borderStyle: hasFile ? "solid" : "dashed",
        }}
      >
        <div className="flex flex-col items-center gap-3 px-6 py-8 text-center">
          {!hasFile ? (
            /* Empty state */
            <>
              <span
                className="flex h-14 w-14 items-center justify-center rounded-2xl"
                style={{ background: "rgba(13,139,141,0.1)", color: "var(--accent)" }}
              >
                <IconUpload />
              </span>
              <div>
                <p className="text-sm font-semibold text-[var(--foreground)]">
                  Arrastra el informe aquí o{" "}
                  <span style={{ color: "var(--accent)" }}>haz clic para seleccionar</span>
                </p>
                <p className="mt-1 text-xs text-[var(--muted)]">
                  PDF, CSV o Excel (.xlsx) · Máx. 20 MB
                </p>
              </div>
            </>
          ) : (
            /* File selected state */
            <div className="flex w-full items-center gap-3">
              <span
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl"
                style={{ background: `${fileIcon(selectedFile.name)}18`, color: fileIcon(selectedFile.name) }}
              >
                <IconFile />
              </span>
              <div className="min-w-0 flex-1 text-left">
                <p className="truncate text-sm font-semibold text-[var(--foreground)]">
                  {selectedFile.name}
                </p>
                <p className="text-xs text-[var(--muted)]">
                  {(selectedFile.size / 1024).toFixed(1)} KB
                </p>
              </div>
              <button
                type="button"
                aria-label="Quitar archivo"
                onClick={(e) => { e.stopPropagation(); handleReset(); }}
                className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full transition-colors hover:bg-black/8"
                style={{ color: "var(--muted)" }}
              >
                <IconClose />
              </button>
            </div>
          )}
        </div>

        {/* Loading shimmer bar */}
        {isLoading && (
          <div className="absolute bottom-0 left-0 h-1 w-full overflow-hidden rounded-b-2xl bg-black/5">
            <div
              className="h-full rounded-full"
              style={{
                background: "var(--accent)",
                animation: "gemini-progress 1.6s ease-in-out infinite",
                width: "40%",
              }}
            />
          </div>
        )}
      </div>

      {/* Hidden native file input */}
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.csv,.xlsx,.xls"
        className="sr-only"
        onChange={handleFileChange}
        aria-hidden="true"
      />

      {/* ── Extract button ── */}
      {hasFile && state !== "success" && (
        <button
          type="button"
          id="btn-extraer-documento"
          onClick={handleExtract}
          disabled={isLoading}
          className="flex w-full items-center justify-center gap-2 rounded-2xl px-5 py-3 text-sm font-semibold text-white transition-all duration-200 disabled:opacity-60"
          style={{
            background: isLoading
              ? "rgba(13,139,141,0.7)"
              : "var(--accent)",
            boxShadow: isLoading ? "none" : "0 4px 16px rgba(13,139,141,0.35)",
          }}
        >
          {isLoading ? (
            <>
              <span
                className="h-4 w-4 rounded-full border-2 border-white/40 border-t-white"
                style={{ animation: "spin 0.75s linear infinite" }}
              />
              Extrayendo datos con IA…
            </>
          ) : (
            "✦ Extraer datos del documento"
          )}
        </button>
      )}

      {/* ── Error message ── */}
      {state === "error" && errorMsg && (
        <div className="flex items-start gap-2.5 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3">
          <span className="mt-0.5 text-rose-500"><IconWarning /></span>
          <p className="text-sm text-rose-700">{errorMsg}</p>
        </div>
      )}

      {/* ── Success summary ── */}
      {state === "success" && result && (
        <div className="space-y-3">
          {/* Extraction stats pill */}
          <div className="flex items-center gap-2 rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3">
            <span className="text-emerald-600"><IconCheck /></span>
            <p className="text-sm font-semibold text-emerald-800">
              {result.extracted_count} de {result.total_fields} campos extraídos del documento.
            </p>
          </div>

          {/* Missing fields warning */}
          {result.missing_fields.length > 0 && (
            <div
              className="rounded-2xl border px-4 py-3 space-y-2"
              style={{
                borderColor: "#fde68a",
                background: "linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)",
              }}
            >
              <div className="flex items-center gap-2">
                <span style={{ color: "#b45309" }}><IconWarning /></span>
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-amber-700">
                  Campos no encontrados — completa manualmente
                </p>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {result.missing_fields.map((field) => (
                  <span
                    key={field}
                    className="rounded-full px-2.5 py-0.5 text-[11px] font-medium"
                    style={{ background: "rgba(180,83,9,0.1)", color: "#92400e" }}
                  >
                    {FIELD_LABELS[field] ?? field}
                  </span>
                ))}
              </div>
              <p className="text-xs text-amber-800">
                Los campos marcados en amarillo dentro del formulario están vacíos. Puedes añadirlos manualmente antes de analizar.
              </p>
            </div>
          )}

          {/* Re-upload option */}
          <button
            type="button"
            onClick={handleReset}
            className="text-xs text-[var(--muted)] underline underline-offset-2 transition-colors hover:text-[var(--foreground)]"
          >
            Cargar otro documento
          </button>
        </div>
      )}

      {/* Privacy notice */}
      <p className="text-[10px] leading-relaxed text-[var(--muted)]">
        El documento se procesa con la capa gratuita de Google AI Studio. No incluyas datos
        personales identificables. Los documentos pueden usarse de forma anónima para mejorar el
        modelo.
      </p>

      {/* Keyframe animations (injected once via a style tag) */}
      <style>{`
        @keyframes gemini-progress {
          0%   { transform: translateX(-100%); }
          50%  { transform: translateX(150%); }
          100% { transform: translateX(400%); }
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
