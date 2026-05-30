"use client";

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
    const raw = Array.isArray(rule.consequent)
      ? String(rule.consequent[1] ?? rule.consequent[0] ?? "")
      : String(rule.consequent ?? "");
    const humanized = raw.replace(/_/g, " ").trim();
    const term = humanized
      ? `${humanized[0].toUpperCase()}${humanized.slice(1)}`
      : "Riesgo";
    return {
      label: `Riesgo ${term}`,
      activation: formatPercent(rule.activation ?? 0),
      weight: rule.weight ?? 1,
    };
  };

  return (
    <div className="mx-auto w-full max-w-6xl px-6 pb-20 pt-6">
      <div className="flex flex-col gap-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="space-y-2">
            <DiseaseBadge label="Resultados" />
            <h1 className="font-display text-4xl font-semibold text-[var(--foreground)]">
              Resumen del analisis
            </h1>
            <p className="max-w-xl text-sm text-[var(--muted)]">
              Visualiza el nivel de riesgo estimado para {disease.shortName} y las
              recomendaciones iniciales.
            </p>
          </div>
          <ButtonLink href="/analyze" size="sm">
            Volver a analizar
          </ButtonLink>
        </div>

        {!result ? (
          <Card className="flex items-center justify-center py-12">
            <Loader label="Cargando resultados" />
          </Card>
        ) : (
          <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
            <ResultCard result={result} disease={disease} />

            <div className="grid gap-6">
              <Card className="space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-[var(--foreground)]">
                    Reglas activadas
                  </h2>
                </div>
                {!result.rules.length ? (
                  <p className="text-sm text-[var(--muted)]">
                    No se activaron reglas con los datos actuales.
                  </p>
                ) : (
                  <ul className="space-y-3 text-sm text-[var(--muted)]">
                    {[...result.rules]
                      .sort(
                        (a, b) =>
                          (b.activation ?? 0) - (a.activation ?? 0)
                      )
                      .map((rule, index) => {
                      const info = formatRule(rule);
                      return (
                        <li
                          key={`${info.label}-${index}`}
                          className="flex items-start justify-between gap-4"
                        >
                          <div>
                            <p className="font-semibold text-[var(--foreground)]">
                              {info.label}
                            </p>
                            <p className="text-xs text-[var(--muted)]">
                              Peso {info.weight}
                            </p>
                          </div>
                          <span className="rounded-full bg-black/5 px-3 py-1 text-xs font-semibold text-[var(--foreground)]">
                            Activacion {info.activation}
                          </span>
                        </li>
                      );
                    })}
                  </ul>
                )}
              </Card>

              <Card className="space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-[var(--foreground)]">
                    Recomendaciones
                  </h2>
                  <Button variant="ghost" size="sm" onClick={() => setOpenModal(true)}>
                    Como interpretar
                  </Button>
                </div>
                <ul className="space-y-3 text-sm text-[var(--muted)]">
                  {result.recommendations.map((item) => (
                    <li key={item} className="flex items-start gap-3">
                      <span className="mt-1 h-2 w-2 rounded-full bg-[var(--accent)]" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </Card>

              <Card className="space-y-3">
                <p className="text-xs uppercase tracking-[0.3em] text-[var(--muted)]">
                  Importante
                </p>
                <h3 className="text-lg font-semibold text-[var(--foreground)]">
                  No es un diagnostico definitivo.
                </h3>
                <p className="text-sm text-[var(--muted)]">
                  Esta herramienta no sustituye la evaluacion de un veterinario.
                  Usa el reporte como apoyo para decidir proximos pasos.
                </p>
              </Card>
            </div>
          </div>
        )}
      </div>

      <Modal
        open={openModal}
        onClose={() => setOpenModal(false)}
        title="Interpretacion del resultado"
      >
        <p>
          El puntaje refleja un riesgo estimado basado en patrones observados. No
          reemplaza pruebas clinicas ni diagnosticos profesionales.
        </p>
      </Modal>
    </div>
  );
}
