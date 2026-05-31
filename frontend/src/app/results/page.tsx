"use client";

import type { CSSProperties } from "react";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { AnalysisResult, buildMockResult } from "@/lib/api";
import { diseases, getDiseaseById } from "@/lib/diseases";
import { formatPercent } from "@/lib/format";
import { Button, ButtonLink } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DiseaseBadge } from "@/components/ui/DiseaseBadge";
import { Loader } from "@/components/ui/Loader";
import { Modal } from "@/components/ui/Modal";
import { ResultCard } from "@/components/ui/ResultCard";

/* ─── Paleta por nivel de riesgo ──────────────────────────────── */
const RISK_COLORS: Record<
  string,
  {
    itemBg: string;
    itemBorder: string;
    badgeBg: string;
    badgeText: string;
    barColor: string;
    dot: string;
  }
> = {
  muy_bajo: {
    itemBg: "linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%)",
    itemBorder: "#a7f3d0",
    badgeBg: "#d1fae5",
    badgeText: "#065f46",
    barColor: "#10b981",
    dot: "#34d399",
  },
  bajo: {
    itemBg: "linear-gradient(135deg, #f0fdfa 0%, #ccfbf1 100%)",
    itemBorder: "#99f6e4",
    badgeBg: "#ccfbf1",
    badgeText: "#115e59",
    barColor: "#14b8a6",
    dot: "#2dd4bf",
  },
  medio: {
    itemBg: "linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)",
    itemBorder: "#fde68a",
    badgeBg: "#fef3c7",
    badgeText: "#92400e",
    barColor: "#f59e0b",
    dot: "#fbbf24",
  },
  alto: {
    itemBg: "linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%)",
    itemBorder: "#fed7aa",
    badgeBg: "#ffedd5",
    badgeText: "#9a3412",
    barColor: "#f97316",
    dot: "#fb923c",
  },
  muy_alto: {
    itemBg: "linear-gradient(135deg, #fff1f2 0%, #ffe4e6 100%)",
    itemBorder: "#fecdd3",
    badgeBg: "#ffe4e6",
    badgeText: "#9f1239",
    barColor: "#f43f5e",
    dot: "#fb7185",
  },
  default: {
    itemBg: "linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%)",
    itemBorder: "#d1d5db",
    badgeBg: "#e5e7eb",
    badgeText: "#374151",
    barColor: "#6b7280",
    dot: "#9ca3af",
  },
};

/* ─── Etiquetas legibles para el nivel de riesgo ─────────────── */
const RISK_LABEL_MAP: Record<string, string> = {
  muy_bajo: "Riesgo muy bajo",
  bajo: "Riesgo bajo",
  medio: "Riesgo medio",
  alto: "Riesgo alto",
  muy_alto: "Riesgo muy alto",
};

export default function ResultsPage() {
  const searchParams = useSearchParams();
  const diseaseId = searchParams.get("d") ?? diseases[0]?.id ?? "cushing";
  const disease = getDiseaseById(diseaseId);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [openModal, setOpenModal] = useState(false);

  useEffect(() => {
    const stored = window.sessionStorage.getItem("analysisResult");
    if (stored) {
      try {
        const parsed = JSON.parse(stored) as AnalysisResult;
        setResult({
          ...parsed,
          rules: Array.isArray(parsed.rules) ? parsed.rules : [],
        });
        return;
      } catch {
        setResult(null);
      }
    }
    setResult(buildMockResult(diseaseId));
  }, [diseaseId]);

  const formatRule = (rule: AnalysisResult["rules"][number]) => {
    // El label descriptivo viene del backend (ej: "Triada clinica principal")
    const providedLabel = (rule as any).label ?? rule.label;

    // El nivel de riesgo se extrae del consecuente (tupla ["riesgo", "muy_bajo"])
    const consequentText = Array.isArray(rule.consequent)
      ? String(rule.consequent[1] ?? rule.consequent[0] ?? "")
      : String(rule.consequent ?? "");

    const riskKey = consequentText
      .trim()
      .toLowerCase()
      .replace(/\s+/g, "_")
      .replace(/-/g, "_");

    // El label descriptivo de la regla es el TÍTULO principal
    // Fallback: usar el nivel de riesgo humanizado si no hay label
    const humanRisk = consequentText.replace(/_/g, " ").trim();
    const humanRiskCap = humanRisk
      ? `${humanRisk[0].toUpperCase()}${humanRisk.slice(1)}`
      : "Regla activada";

    const ruleTitle =
      providedLabel && String(providedLabel).trim().length > 0
        ? String(providedLabel)
        : `Regla de riesgo ${humanRiskCap.toLowerCase()}`;

    const tone = RISK_COLORS[riskKey] ?? RISK_COLORS.default;
    const riskLabel = RISK_LABEL_MAP[riskKey] ?? `Riesgo ${consequentText.replace(/_/g, " ")}`;

    return {
      ruleTitle,
      riskLabel,
      activation: rule.activation ?? 0,
      activationText: formatPercent(rule.activation ?? 0),
      weight: rule.weight ?? 1,
      tone,
    };
  };

  const sortedRules = result
    ? [...result.rules].sort((a, b) => (b.activation ?? 0) - (a.activation ?? 0))
    : [];

  return (
    <div className="mx-auto w-full max-w-6xl px-6 pb-20 pt-6">
      <div className="flex flex-col gap-6">

        {/* ── Cabecera ── */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="space-y-2">
            <DiseaseBadge label="Resultados" />
            <h1 className="font-display text-4xl font-semibold text-[var(--foreground)]">
              Resumen del análisis
            </h1>
            <p className="max-w-xl text-sm text-[var(--muted)]">
              Nivel de riesgo estimado para{" "}
              <span className="font-semibold text-[var(--foreground)]">{disease.shortName}</span>{" "}
              y recomendaciones iniciales.
            </p>
          </div>
          <ButtonLink href="/analyze" size="sm" variant="secondary">
            ← Volver a analizar
          </ButtonLink>
        </div>

        {!result ? (
          <Card className="flex items-center justify-center py-16">
            <Loader label="Cargando resultados…" />
          </Card>
        ) : (
          <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">

            {/* ── Columna izquierda ── */}
            <div className="grid gap-6 content-start">
              <ResultCard result={result} disease={disease} />

              {/* Recomendaciones */}
              <Card className="space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-[var(--foreground)]">
                    Recomendaciones
                  </h2>
                  <Button variant="ghost" size="sm" onClick={() => setOpenModal(true)}>
                    Cómo interpretar
                  </Button>
                </div>
                <ul className="space-y-3">
                  {result.recommendations.map((item) => (
                    <li key={item} className="flex items-start gap-3">
                      <span
                        className="mt-1.5 h-2 w-2 shrink-0 rounded-full"
                        style={{ backgroundColor: "var(--accent)" }}
                      />
                      <span className="text-sm text-[var(--muted)]">{item}</span>
                    </li>
                  ))}
                </ul>
              </Card>

              {/* Aviso */}
              <Card
                className="space-y-2"
                style={{
                  background:
                    "linear-gradient(135deg, rgba(13,139,141,0.07) 0%, rgba(13,139,141,0.03) 100%)",
                  borderColor: "rgba(13,139,141,0.2)",
                } as CSSProperties}
              >
                <p className="text-xs font-semibold uppercase tracking-[0.3em] text-[var(--accent)]">
                  Importante
                </p>
                <h3 className="text-base font-semibold text-[var(--foreground)]">
                  No es un diagnóstico definitivo.
                </h3>
                <p className="text-sm text-[var(--muted)]">
                  Esta herramienta no sustituye la evaluación de un veterinario. Usa el reporte como
                  apoyo para decidir próximos pasos.
                </p>
              </Card>
            </div>

            {/* ── Columna derecha: Reglas activadas ── */}
            <div className="grid content-start gap-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-[var(--foreground)]">
                    Reglas activadas
                  </h2>
                  <p className="text-xs text-[var(--muted)]">
                    {sortedRules.length} regla{sortedRules.length !== 1 ? "s" : ""} disparada
                    {sortedRules.length !== 1 ? "s" : ""} · ordenadas por activación
                  </p>
                </div>
                {sortedRules.length > 0 && (
                  <span
                    className="rounded-full px-3 py-1 text-xs font-semibold"
                    style={{ background: "rgba(13,139,141,0.12)", color: "var(--accent)" }}
                  >
                    {sortedRules.length}
                  </span>
                )}
              </div>

              {!sortedRules.length ? (
                <Card>
                  <p className="text-sm text-[var(--muted)]">
                    No se activaron reglas con los datos actuales.
                  </p>
                </Card>
              ) : (
                <ul className="space-y-3">
                  {sortedRules.map((rule, index) => {
                    const info = formatRule(rule);
                    const activationPct = Math.round(info.activation * 100);
                    return (
                      <li
                        key={`${info.ruleTitle}-${index}`}
                        className="rounded-2xl border p-4 transition-shadow hover:shadow-md"
                        style={{
                          background: info.tone.itemBg,
                          borderColor: info.tone.itemBorder,
                        }}
                      >
                        {/* Fila superior: badge de nivel + activación */}
                        <div className="mb-3 flex items-center justify-between gap-3">
                          <span
                            className="inline-flex rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-[0.12em]"
                            style={{
                              backgroundColor: info.tone.badgeBg,
                              color: info.tone.badgeText,
                            }}
                          >
                            {info.riskLabel}
                          </span>
                          <span
                            className="text-xs font-semibold tabular-nums"
                            style={{ color: info.tone.badgeText }}
                          >
                            {info.activationText}
                          </span>
                        </div>

                        {/* Título principal: el label descriptivo de la regla */}
                        <p className="mb-2 text-sm font-semibold leading-snug text-[var(--foreground)]">
                          {info.ruleTitle}
                        </p>

                        {/* Barra de activación */}
                        <div
                          className="h-1.5 w-full overflow-hidden rounded-full"
                          style={{ backgroundColor: `${info.tone.itemBorder}55` }}
                        >
                          <div
                            className="h-full rounded-full transition-all duration-500"
                            style={{
                              width: `${activationPct}%`,
                              backgroundColor: info.tone.barColor,
                            }}
                          />
                        </div>

                        {/* Fila inferior: peso */}
                        <div className="mt-2 flex items-center gap-1.5">
                          <span
                            className="h-1.5 w-1.5 rounded-full"
                            style={{ backgroundColor: info.tone.dot }}
                          />
                          <span className="text-[11px] text-[var(--muted)]">
                            Peso de regla: {info.weight}
                          </span>
                        </div>
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>
          </div>
        )}
      </div>

      <Modal
        open={openModal}
        onClose={() => setOpenModal(false)}
        title="Interpretación del resultado"
      >
        <p>
          El puntaje refleja un riesgo estimado basado en patrones observados. No reemplaza pruebas
          clínicas ni diagnósticos profesionales.
        </p>
      </Modal>
    </div>
  );
}
