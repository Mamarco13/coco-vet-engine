"use client";

import { useEffect, useRef, useState } from "react";
import { extractVoiceData, ExtractionResult } from "@/lib/api";
import type { ExtractedFormData } from "@/components/ui/DocumentUploader";

// ─── Tipos ─────────────────────────────────────────────────────────────────────

type VoiceState = "idle" | "listening" | "processing" | "success" | "error";

type Props = {
  /** Same callback signature as DocumentUploader so both feed the same handler. */
  onExtracted: (data: ExtractedFormData, missingFields: string[]) => void;
};

// ─── Web Speech API browser types ──────────────────────────────────────────────

declare global {
  interface Window {
    SpeechRecognition: typeof SpeechRecognition;
    webkitSpeechRecognition: typeof SpeechRecognition;
  }
}

// ─── Iconos inline ─────────────────────────────────────────────────────────────

const IconMic = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
    <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
    <line x1="12" y1="19" x2="12" y2="23" />
    <line x1="8" y1="23" x2="16" y2="23" />
  </svg>
);

const IconStop = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
    <rect x="4" y="4" width="16" height="16" rx="2" />
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

// ─── Etiquetas legibles de los campos ──────────────────────────────────────────

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

// ─── Componente ────────────────────────────────────────────────────────────────

export function VoiceRecorder({ onExtracted }: Props) {
  const [state, setState] = useState<VoiceState>("idle");
  const [transcript, setTranscript] = useState("");
  const [interimText, setInterimText] = useState("");
  const [result, setResult] = useState<ExtractionResult | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [browserSupported, setBrowserSupported] = useState(true);

  const recognitionRef = useRef<SpeechRecognition | null>(null);
  // Ref that mirrors `transcript` state — always has the latest value
  // synchronously, even inside recognition event callbacks.
  const transcriptRef = useRef("");

  // Check browser support on mount
  useEffect(() => {
    const SR = window.SpeechRecognition ?? window.webkitSpeechRecognition;
    if (!SR) setBrowserSupported(false);
  }, []);

  // ── Start / stop recording ──────────────────────────────────────────────────

  function startListening() {
    const SR = window.SpeechRecognition ?? window.webkitSpeechRecognition;
    if (!SR) return;

    const recognition = new SR();
    recognition.lang = "es-ES";
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setState("listening");
      setTranscript("");
      setInterimText("");
      transcriptRef.current = "";   // reset ref too
      setResult(null);
      setErrorMsg(null);
    };

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let finalPart = "";
      let interimPart = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const text = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalPart += text + " ";
        } else {
          interimPart += text;
        }
      }
      if (finalPart) {
        transcriptRef.current += finalPart;          // sync ref update first
        setTranscript(transcriptRef.current);         // then React state
      }
      setInterimText(interimPart);
    };

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      if (event.error === "no-speech") return; // ignore silence
      setErrorMsg(`Error de reconocimiento: ${event.error}`);
      setState("error");
    };

    // onend fires after stop() — flush any remaining interim text into the ref
    recognition.onend = () => {
      setInterimText("");
    };

    recognitionRef.current = recognition;
    recognition.start();
  }

  function stopListening() {
    recognitionRef.current?.stop();
    recognitionRef.current = null;
  }

  async function handleStop() {
    const recognition = recognitionRef.current;

    if (!recognition) {
      // Already stopped — just read what we have in the ref
      processTranscript(transcriptRef.current);
      return;
    }

    // Wait for recognition.onend before reading the final transcript,
    // so any pending onresult events have time to flush.
    await new Promise<void>((resolve) => {
      recognition.onend = () => {
        setInterimText("");
        resolve();
      };
      recognition.stop();
      recognitionRef.current = null;
    });

    processTranscript(transcriptRef.current);
  }

  async function processTranscript(raw: string) {
    const finalTranscript = raw.trim();
    if (!finalTranscript) {
      setErrorMsg("No se capturó ningún texto. Intenta hablar más cerca del micrófono.");
      setState("error");
      return;
    }

    // Make sure the displayed transcript matches what we send
    setTranscript(finalTranscript);

    setState("processing");
    try {
      const data = await extractVoiceData(finalTranscript);
      setResult(data);
      setState("success");

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

  function handleReset() {
    recognitionRef.current?.stop();
    recognitionRef.current = null;
    transcriptRef.current = "";
    setState("idle");
    setTranscript("");
    setInterimText("");
    setResult(null);
    setErrorMsg(null);
  }

  // ── Render ──────────────────────────────────────────────────────────────────

  if (!browserSupported) {
    return (
      <div className="flex items-start gap-2.5 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3">
        <span className="mt-0.5 text-amber-500"><IconWarning /></span>
        <p className="text-sm text-amber-700">
          Tu navegador no soporta el reconocimiento de voz. Usa Chrome o Edge para esta función.
        </p>
      </div>
    );
  }

  const isListening = state === "listening";
  const isProcessing = state === "processing";
  const displayText = transcript + interimText;

  return (
    <div className="space-y-3">

      {/* ── Botón principal ── */}
      <div
        className="relative overflow-hidden rounded-2xl border-2 transition-all duration-300"
        style={{
          borderColor: isListening
            ? "var(--accent)"
            : state === "success"
            ? "rgba(16,185,129,0.4)"
            : state === "error"
            ? "rgba(239,68,68,0.35)"
            : "rgba(0,0,0,0.1)",
          background: isListening
            ? "rgba(13,139,141,0.04)"
            : state === "success"
            ? "linear-gradient(135deg, rgba(16,185,129,0.05) 0%, rgba(16,185,129,0.02) 100%)"
            : "rgba(255,255,255,0.7)",
          borderStyle: isListening ? "solid" : "dashed",
        }}
      >
        <div className="flex flex-col items-center gap-3 px-6 py-6 text-center">

          {/* Icono de micrófono con anillo de pulso */}
          <div className="relative flex items-center justify-center">
            {isListening && (
              <>
                <span className="absolute h-16 w-16 rounded-full" style={{ background: "rgba(13,139,141,0.12)", animation: "voice-pulse 1.4s ease-out infinite" }} />
                <span className="absolute h-12 w-12 rounded-full" style={{ background: "rgba(13,139,141,0.18)", animation: "voice-pulse 1.4s ease-out 0.3s infinite" }} />
              </>
            )}
            <span
              className="relative flex h-14 w-14 items-center justify-center rounded-2xl transition-all duration-300"
              style={{
                background: isListening
                  ? "var(--accent)"
                  : state === "success"
                  ? "rgba(16,185,129,0.15)"
                  : "rgba(13,139,141,0.1)",
                color: isListening
                  ? "white"
                  : state === "success"
                  ? "#059669"
                  : "var(--accent)",
              }}
            >
              <IconMic />
            </span>
          </div>

          {/* Texto de estado */}
          {state === "idle" && (
            <div>
              <p className="text-sm font-semibold text-[var(--foreground)]">
                Dicta los datos del paciente
              </p>
              <p className="mt-1 text-xs text-[var(--muted)]">
                Habla con naturalidad — Gemini interpretará el lenguaje clínico
              </p>
            </div>
          )}

          {isListening && (
            <div>
              <p className="text-sm font-semibold" style={{ color: "var(--accent)" }}>
                Escuchando…
              </p>
              {displayText ? (
                <p className="mt-1 max-w-xs text-xs leading-relaxed text-[var(--muted)] italic">
                  &ldquo;{displayText}&rdquo;
                </p>
              ) : (
                <p className="mt-1 text-xs text-[var(--muted)]">Comienza a hablar sobre el paciente</p>
              )}
            </div>
          )}

          {isProcessing && (
            <div>
              <p className="text-sm font-semibold text-[var(--foreground)]">
                Analizando con Gemini…
              </p>
              <p className="mt-1 text-xs text-[var(--muted)]">Interpretando el dictado</p>
            </div>
          )}

          {state === "success" && (
            <p className="text-sm font-semibold" style={{ color: "#059669" }}>
              ¡Dictado procesado correctamente!
            </p>
          )}
        </div>

        {/* Barra de progreso shimmer durante procesado */}
        {isProcessing && (
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

      {/* ── Botones de acción ── */}
      {state === "idle" && (
        <button
          type="button"
          id="btn-iniciar-voz"
          onClick={startListening}
          className="flex w-full items-center justify-center gap-2 rounded-2xl px-5 py-3 text-sm font-semibold text-white transition-all duration-200"
          style={{
            background: "var(--accent)",
            boxShadow: "0 4px 16px rgba(13,139,141,0.35)",
          }}
        >
          <IconMic />
          Iniciar dictado por voz
        </button>
      )}

      {isListening && (
        <button
          type="button"
          id="btn-detener-voz"
          onClick={handleStop}
          className="flex w-full items-center justify-center gap-2 rounded-2xl px-5 py-3 text-sm font-semibold text-white transition-all duration-200"
          style={{
            background: "#e11d48",
            boxShadow: "0 4px 16px rgba(225,29,72,0.35)",
          }}
        >
          <IconStop />
          Detener y procesar
        </button>
      )}

      {/* ── Error ── */}
      {state === "error" && errorMsg && (
        <div className="flex items-start gap-2.5 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3">
          <span className="mt-0.5 text-rose-500"><IconWarning /></span>
          <div className="flex-1">
            <p className="text-sm text-rose-700">{errorMsg}</p>
            <button
              type="button"
              onClick={handleReset}
              className="mt-1.5 text-xs text-rose-600 underline underline-offset-2"
            >
              Intentar de nuevo
            </button>
          </div>
        </div>
      )}

      {/* ── Resumen de éxito ── */}
      {state === "success" && result && (
        <div className="space-y-3">
          {/* Stats pill */}
          <div className="flex items-center gap-2 rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3">
            <span className="text-emerald-600"><IconCheck /></span>
            <p className="text-sm font-semibold text-emerald-800">
              {result.extracted_count} de {result.total_fields} campos extraídos del dictado.
            </p>
          </div>

          {/* Transcripción final */}
          {transcript && (
            <div
              className="rounded-2xl border px-4 py-3"
              style={{ borderColor: "rgba(0,0,0,0.08)", background: "rgba(0,0,0,0.02)" }}
            >
              <p className="mb-1 text-[10px] font-bold uppercase tracking-[0.2em] text-[var(--muted)]">
                Transcripción detectada
              </p>
              <p className="text-xs leading-relaxed text-[var(--foreground)] italic">
                &ldquo;{transcript.trim()}&rdquo;
              </p>
            </div>
          )}

          {/* Campos no encontrados */}
          {result.missing_fields.length > 0 && (
            <div
              className="rounded-2xl border px-4 py-3 space-y-2"
              style={{ borderColor: "#fde68a", background: "linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)" }}
            >
              <div className="flex items-center gap-2">
                <span style={{ color: "#b45309" }}><IconWarning /></span>
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-amber-700">
                  Campos no mencionados — completa manualmente
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
            </div>
          )}

          <button
            type="button"
            onClick={handleReset}
            className="text-xs text-[var(--muted)] underline underline-offset-2 transition-colors hover:text-[var(--foreground)]"
          >
            Nuevo dictado
          </button>
        </div>
      )}

      {/* Aviso de privacidad */}
      <p className="text-[10px] leading-relaxed text-[var(--muted)]">
        🎙️ La transcripción se realiza localmente en tu navegador. El texto se envía a la API de
        Gemini para interpretar los campos clínicos. No incluyas datos de identificación personal.
      </p>

      {/* Keyframes */}
      <style>{`
        @keyframes voice-pulse {
          0%   { transform: scale(0.85); opacity: 0.7; }
          70%  { transform: scale(1.6);  opacity: 0; }
          100% { transform: scale(1.6);  opacity: 0; }
        }
        @keyframes gemini-progress {
          0%   { transform: translateX(-100%); }
          50%  { transform: translateX(150%); }
          100% { transform: translateX(400%); }
        }
      `}</style>
    </div>
  );
}
