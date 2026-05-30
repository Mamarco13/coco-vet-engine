"use client";

import Image from "next/image";
import { ChangeEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { analyzeCushing } from "@/lib/api";
import { diseases } from "@/lib/diseases";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DiseaseBadge } from "@/components/ui/DiseaseBadge";
import { Loader } from "@/components/ui/Loader";
import { Modal } from "@/components/ui/Modal";
import { ProgressBar } from "@/components/ui/ProgressBar";

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

export default function AnalyzePage() {
  const router = useRouter();
  const [selectedDisease, setSelectedDisease] = useState(diseases[0].id);
  const [form, setForm] = useState<CushingFormState>(initialForm);
  const [error, setError] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);

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
      const result = await analyzeCushing({
        diseaseId: selectedDisease,
        payload,
      });
      window.sessionStorage.setItem("analysisResult", JSON.stringify(result));
      setProgress(100);
      router.push(`/results?d=${result.diseaseId}`);
    } catch (analysisError) {
      setError("No se pudo completar el analisis. Intenta nuevamente.");
    } finally {
      window.clearInterval(timer);
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="mx-auto w-full max-w-6xl px-6 pb-20 pt-6">
      <div className="flex flex-col gap-8 lg:flex-row lg:items-start">
        <div className="flex-1 space-y-6">
          <DiseaseBadge label="Analisis" />
          <h1 className="font-display text-4xl font-semibold text-[var(--foreground)]">
            Analisis clinico basado en parametros.
          </h1>
          <p className="max-w-xl text-sm text-[var(--muted)]">
            Completa datos demograficos, clinicos y de laboratorio para estimar el
            riesgo con el motor difuso.
          </p>

          <Card className="space-y-6">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-[var(--muted)]">
                  Enfermedad
                </p>
                <h2 className="text-lg font-semibold text-[var(--foreground)]">
                  Seleccion actual
                </h2>
              </div>
              <select
                value={selectedDisease}
                onChange={(event) => setSelectedDisease(event.target.value)}
                className="rounded-full border border-black/10 bg-white/70 px-4 py-2 text-sm font-semibold text-[var(--foreground)]"
              >
                {diseases.map((disease) => (
                  <option key={disease.id} value={disease.id}>
                    {disease.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <label className="text-xs uppercase tracking-[0.3em] text-[var(--muted)]">
                  Edad del perro
                </label>
                <input
                  type="number"
                  min="0"
                  step="0.1"
                  value={form.edad}
                  onChange={handleText("edad")}
                  placeholder="Ej: 8"
                  className="w-full rounded-2xl border border-black/10 bg-white/70 px-4 py-2 text-sm text-[var(--foreground)]"
                />
                <p className="text-xs text-[var(--muted)]">
                  Edad aproximada en formato decimal.
                </p>
              </div>
              <div className="space-y-2">
                <label className="text-xs uppercase tracking-[0.3em] text-[var(--muted)]">
                  Raza
                </label>
                <input
                  type="text"
                  value={form.raza}
                  onChange={handleText("raza")}
                  className="w-full rounded-2xl border border-black/10 bg-white/70 px-4 py-2 text-sm text-[var(--foreground)]"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs uppercase tracking-[0.3em] text-[var(--muted)]">
                  Peso relativo
                </label>
                <input
                  type="number"
                  min="0"
                  step="1"
                  value={form.peso}
                  onChange={handleText("peso")}
                  placeholder="Ej: 120"
                  className="w-full rounded-2xl border border-black/10 bg-white/70 px-4 py-2 text-sm text-[var(--foreground)]"
                />
                <p className="text-xs text-[var(--muted)]">
                  Porcentaje respecto a la media de su raza.
                </p>
              </div>
            </div>

            <div className="space-y-3">
              <p className="text-xs uppercase tracking-[0.3em] text-[var(--muted)]">
                Signos clinicos
              </p>
              <div className="grid gap-3 sm:grid-cols-2">
                {(
                  [
                    { key: "polidipsia", label: "Polidipsia" },
                    { key: "abdomen_inflamado", label: "Abdomen inflamado" },
                    { key: "alopecia", label: "Alopecia" },
                    { key: "polifagia", label: "Polifagia" },
                    { key: "poliuria", label: "Poliuria" },
                    { key: "debilidad", label: "Debilidad muscular" },
                    { key: "piel_fina", label: "Piel fina" },
                    { key: "jadeo", label: "Jadeo" },
                  ] as Array<{ key: ClinicalKey; label: string }>
                ).map((item) => (
                  <label
                    key={item.key}
                    className="flex items-center gap-3 rounded-2xl border border-black/10 bg-white/60 px-4 py-2 text-sm text-[var(--foreground)]"
                  >
                    <input
                      type="checkbox"
                      checked={form[item.key]}
                      onChange={handleCheck(item.key)}
                      className="h-4 w-4"
                    />
                    {item.label}
                  </label>
                ))}
              </div>
            </div>

            <div className="space-y-3">
              <p className="text-xs uppercase tracking-[0.3em] text-[var(--muted)]">
                Laboratorio
              </p>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <label className="text-xs uppercase tracking-[0.3em] text-[var(--muted)]">
                    ALP (U/L)
                  </label>
                  <input
                    type="number"
                    min="0"
                    step="1"
                    value={form.alp}
                    onChange={handleText("alp")}
                    className="w-full rounded-2xl border border-black/10 bg-white/70 px-4 py-2 text-sm text-[var(--foreground)]"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-xs uppercase tracking-[0.3em] text-[var(--muted)]">
                    ALT (U/L)
                  </label>
                  <input
                    type="number"
                    min="0"
                    step="1"
                    value={form.alt}
                    onChange={handleText("alt")}
                    className="w-full rounded-2xl border border-black/10 bg-white/70 px-4 py-2 text-sm text-[var(--foreground)]"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-xs uppercase tracking-[0.3em] text-[var(--muted)]">
                    USG
                  </label>
                  <input
                    type="number"
                    min="0"
                    step="0.001"
                    value={form.usg}
                    onChange={handleText("usg")}
                    className="w-full rounded-2xl border border-black/10 bg-white/70 px-4 py-2 text-sm text-[var(--foreground)]"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-xs uppercase tracking-[0.3em] text-[var(--muted)]">
                    Colesterol (mg/dL)
                  </label>
                  <input
                    type="number"
                    min="0"
                    step="1"
                    value={form.colesterol}
                    onChange={handleText("colesterol")}
                    className="w-full rounded-2xl border border-black/10 bg-white/70 px-4 py-2 text-sm text-[var(--foreground)]"
                  />
                </div>
              </div>
            </div>

            {error && (
              <p className="text-sm text-rose-600" role="alert">
                {error}
              </p>
            )}
          </Card>
        </div>

        <div className="w-full max-w-sm space-y-6">
          <Card className="space-y-4">
            <h3 className="text-base font-semibold text-[var(--foreground)]">
              Checklist antes de enviar
            </h3>
            <ul className="space-y-3 text-sm text-[var(--muted)]">
              <li>• Verifica edad, peso y raza.</li>
              <li>• Confirma laboratorio y signos clinicos.</li>
              <li>• Completa todos los campos obligatorios.</li>
            </ul>
            <Button
              size="lg"
              onClick={startAnalysis}
              isLoading={isAnalyzing}
              disabled={isAnalyzing}
            >
              Analizar ahora
            </Button>
            <p className="text-xs text-[var(--muted)]">
              Esta herramienta no sustituye la evaluacion de un veterinario.
            </p>
          </Card>

          <Card className="space-y-3">
            <div className="flex items-center gap-3">
              <Image src="/pata.png" alt="Pata" width={28} height={28} />
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-[var(--muted)]">
                  Tiempo estimado
                </p>
                <p className="text-base font-semibold text-[var(--foreground)]">
                  1 - 2 minutos
                </p>
              </div>
            </div>
            <p className="text-sm text-[var(--muted)]">
              El analisis se realiza en la nube y genera un reporte automatico.
            </p>
          </Card>
        </div>
      </div>

      <Modal
        open={isAnalyzing}
        onClose={() => {}}
        dismissible={false}
        title="Analizando"
      >
        <div className="space-y-4">
          <Loader label="Procesando parametros" />
          <ProgressBar value={progress} max={100} />
          <p>
            Estamos evaluando criterios clinicos y de laboratorio. Esto puede
            tardar unos segundos.
          </p>
        </div>
      </Modal>
    </div>
  );
}
