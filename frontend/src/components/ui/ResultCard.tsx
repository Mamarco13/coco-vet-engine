import { AnalysisResult } from "@/lib/api";
import { Disease } from "@/lib/diseases";
import { formatPercent, formatScore } from "@/lib/format";
import { cn } from "@/lib/utils";
import { Card } from "./Card";
import { ProgressBar } from "./ProgressBar";

const toneByLabel: Record<string, string> = {
  "Muy bajo": "text-emerald-700",
  Bajo: "text-emerald-700",
  Medio: "text-amber-700",
  Alto: "text-orange-700",
  "Muy alto": "text-rose-700",
};

export function ResultCard({
  result,
  disease,
}: {
  result: AnalysisResult;
  disease: Disease;
}) {
  const tone = toneByLabel[result.label] ?? "text-[var(--foreground)]";

  return (
    <Card className="grid gap-6">
      <div>
        <p className="text-xs uppercase tracking-[0.3em] text-[var(--muted)]">
          Resultado para {disease.shortName}
        </p>
        <div className="mt-3 flex flex-wrap items-end gap-4">
          <h2 className={cn("text-3xl font-semibold", tone)}>{result.label}</h2>
          <span className="text-sm text-[var(--muted)]">
            Puntaje {formatScore(result.score)}
          </span>
        </div>
      </div>
      <div className="grid gap-2">
        <div className="flex items-center justify-between text-sm text-[var(--muted)]">
          <span>Probabilidad estimada</span>
          <span className="font-semibold text-[var(--foreground)]">
            {formatPercent(result.score)}
          </span>
        </div>
        <ProgressBar value={result.score * 100} />
      </div>
      <div className="grid gap-2 text-sm text-[var(--muted)]">
        <div className="flex items-center justify-between">
          <span>Confianza del motor</span>
          <span className="font-semibold text-[var(--foreground)]">
            {formatPercent(result.confidence)}
          </span>
        </div>
        <p>{result.summary}</p>
      </div>
    </Card>
  );
}
