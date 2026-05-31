"use client";

import Image from "next/image";
import { motion } from "framer-motion";
import { useState } from "react";
import CocoImg from "../../public/Coco.jpeg";
import pataImg from "../../public/pata.png";
import { diseases } from "@/lib/diseases";
import { Button, ButtonLink } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DiseaseBadge } from "@/components/ui/DiseaseBadge";
import { Modal } from "@/components/ui/Modal";

const heroHighlights = [
  {
    label: "Codigo abierto",
    value: "Modelos y reglas auditables",
  },
  {
    label: "Logica difusa",
    value: "Evidencia cientifica aplicada",
  },
  {
    label: "Prevencion",
    value: "Riesgo y guias accionables",
  },
];

const pillars = [
  {
    title: "Base cientifica",
    description:
      "Traducimos literatura clinica en variables claras y medibles.",
  },
  {
    title: "Arquitectura extensible",
    description:
      "Estructura modular para sumar nuevas enfermedades sin rehacer todo.",
  },
  {
    title: "Transparencia explicable",
    description:
      "Cada prediccion se entiende con reglas, contexto y trazabilidad.",
  },
];

const steps = [
  {
    title: "Curacion de evidencia",
    description:
      "Sintetizamos papers y guias clinicas en variables observables.",
  },
  {
    title: "Modelado difuso",
    description:
      "Definimos funciones de pertenencia y reglas interpretables.",
  },
  {
    title: "Prediccion y prevencion",
    description:
      "Entregamos riesgo estimado y recomendaciones de seguimiento.",
  },
];

const modules = [
  {
    title: "Clinico",
    description: "Sintomas, historial y observaciones del cuidador.",
  },
  {
    title: "Laboratorio",
    description: "Resultados objetivos para robustecer la decision.",
  },
  {
    title: "Demografico",
    description: "Edad, raza y contexto para ajustar el riesgo.",
  },
];

const benefits = [
  "Capa explicable para clinicos y tutores",
  "Diseno pensado para escalar a otras patologias",
  "Soporte para prevencion y seguimiento continuo",
  "Indicadores visuales para decisiones informadas",
];

export default function Home() {
  const disease = diseases[0];
  const [openModal, setOpenModal] = useState(false);

  return (
    <div className="pb-20">
      <section className="relative overflow-hidden">
        <div className="pointer-events-none absolute -left-32 top-16 h-72 w-72 rounded-full bg-[radial-gradient(circle,_rgba(13,139,141,0.3),_transparent_65%)]" />
        <div className="pointer-events-none absolute -right-40 -top-24 h-96 w-96 rounded-full bg-[radial-gradient(circle,_rgba(247,215,170,0.45),_transparent_70%)]" />
        <div className="pointer-events-none absolute inset-x-0 top-0 h-40 bg-[linear-gradient(180deg,_rgba(255,255,255,0.7),_transparent)]" />
        <div className="relative mx-auto flex w-full max-w-6xl flex-col gap-12 px-6 pt-12 lg:grid lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="space-y-6"
        >
          <div className="flex flex-wrap items-center gap-3">
            <DiseaseBadge label={disease.name} />
            <span className="rounded-full border border-black/10 bg-white/70 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-[var(--foreground)]">
              Codigo abierto
            </span>
          </div>
          <h1 className="text-balance font-display text-4xl font-semibold text-[var(--foreground)] sm:text-5xl lg:text-6xl">
            Plataforma abierta para predecir y prevenir enfermedades con logica
            difusa aplicada a la evidencia cientifica.
          </h1>
          <p className="max-w-xl text-base text-[var(--muted)] sm:text-lg">
            COCO es un framework extensible: empezamos con Cushing, pero esta hecho
            para sumar nuevas patologias, equipos clinicos y comunidades de
            investigacion.
          </p>
          <div className="flex flex-wrap items-center gap-4">
            <ButtonLink href="/analyze" size="lg">
              Analizar caso
            </ButtonLink>
            <Button variant="secondary" size="lg" onClick={() => setOpenModal(true)}>
              Ver metodologia
            </Button>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            {heroHighlights.map((item) => (
              <div
                key={item.label}
                className="rounded-2xl border border-white/60 bg-white/80 px-4 py-3 text-xs shadow-[0_12px_30px_rgba(15,30,30,0.12)]"
              >
                <p className="text-[0.6rem] uppercase tracking-[0.3em] text-[var(--muted)]">
                  {item.label}
                </p>
                <p className="mt-2 text-sm font-semibold text-[var(--foreground)]">
                  {item.value}
                </p>
              </div>
            ))}
          </div>
          <p className="text-xs text-[var(--muted)]">
            Esta herramienta no sustituye la opinion de un profesional.
          </p>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="relative"
        >
          <div className="absolute -left-6 top-6 hidden h-24 w-24 rounded-3xl bg-[var(--accent-2)] lg:block" />
          <div className="glass grid-dots relative rounded-[32px] p-4">
            <Image
              src={CocoImg}
              alt="Perro en revision"
              width={480}
              height={520}
              priority
              className="h-[420px] w-full rounded-[24px] object-cover"
            />
          </div>
          <div className="absolute -right-4 top-10 hidden rounded-3xl border border-white/70 bg-white/80 px-5 py-4 text-xs shadow-[0_16px_40px_rgba(15,30,30,0.16)] lg:block">
            <p className="uppercase tracking-[0.3em] text-[var(--muted)]">Comunidad</p>
            <p className="mt-2 text-sm font-semibold text-[var(--foreground)]">
              Extensible por diseno
            </p>
          </div>
        </motion.div>
        </div>
      </section>

      <section className="mx-auto mt-20 w-full max-w-6xl px-6">
        <div className="grid gap-6 md:grid-cols-3">
          {pillars.map((card) => (
            <motion.div
              key={card.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4 }}
            >
              <Card className="h-full">
                <h3 className="text-lg font-semibold text-[var(--foreground)]">
                  {card.title}
                </h3>
                <p className="mt-2 text-sm text-[var(--muted)]">{card.description}</p>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>

      <section className="mx-auto mt-20 w-full max-w-6xl px-6">
        <div className="grid gap-8 lg:grid-cols-[0.9fr_1.1fr]">
          <div className="space-y-4">
            <p className="text-xs uppercase tracking-[0.3em] text-[var(--muted)]">
              Metodologia
            </p>
            <h2 className="font-display text-3xl font-semibold text-[var(--foreground)]">
              De la evidencia clinica a una prediccion explicable.
            </h2>
            <p className="text-sm text-[var(--muted)]">
              Cada etapa esta pensada para aportar claridad y trazabilidad, desde la
              literatura cientifica hasta el reporte final.
            </p>
          </div>
          <div className="grid gap-4">
            {steps.map((step, index) => (
              <Card key={step.title} className="flex items-start gap-4">
                <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-[var(--accent-2)] text-sm font-semibold text-[var(--foreground)]">
                  0{index + 1}
                </span>
                <div>
                  <h3 className="text-base font-semibold text-[var(--foreground)]">
                    {step.title}
                  </h3>
                  <p className="text-sm text-[var(--muted)]">{step.description}</p>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto mt-20 w-full max-w-6xl px-6">
        <div className="grid items-center gap-10 lg:grid-cols-[1.1fr_0.9fr]">
          <Card className="space-y-4">
            <h2 className="font-display text-3xl font-semibold text-[var(--foreground)]">
              Cushing hoy, mas enfermedades manana.
            </h2>
            <p className="text-sm text-[var(--muted)]">{disease.description}</p>
            <div className="grid gap-3 text-sm text-[var(--muted)]">
              {benefits.map((benefit) => (
                <div key={benefit} className="flex items-center gap-3">
                  <span className="h-2 w-2 rounded-full bg-[var(--accent)]" />
                  <span>{benefit}</span>
                </div>
              ))}
            </div>
          </Card>
          <div className="relative">
            <div className="glass absolute -left-6 -top-6 hidden h-24 w-24 rounded-3xl lg:block" />
            <div className="glass rounded-[32px] p-6">
              <Image src={pataImg} alt="Icono pata" width={64} height={64} />
              <h3 className="mt-6 text-lg font-semibold text-[var(--foreground)]">
                Plataforma modular por capas
              </h3>
              <p className="mt-2 text-sm text-[var(--muted)]">
                Disenada para sumar variables clinicas, reglas y paquetes de
                patologias sin perder consistencia en la experiencia.
              </p>
              <ButtonLink href="/analyze" className="mt-6">
                Comenzar analisis
              </ButtonLink>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto mt-20 w-full max-w-6xl px-6">
        <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          <div className="space-y-4">
            <p className="text-xs uppercase tracking-[0.3em] text-[var(--muted)]">
              Modulos
            </p>
            <h2 className="font-display text-3xl font-semibold text-[var(--foreground)]">
              Arquitectura lista para crecer con la comunidad.
            </h2>
            <p className="text-sm text-[var(--muted)]">
              Cada modulo aporta una capa de conocimiento y se integra con la logica
              difusa para mantener explicabilidad.
            </p>
          </div>
          <div className="grid gap-4 sm:grid-cols-3">
            {modules.map((module) => (
              <Card key={module.title} className="h-full">
                <p className="text-xs uppercase tracking-[0.3em] text-[var(--muted)]">
                  {module.title}
                </p>
                <p className="mt-3 text-sm text-[var(--foreground)]">
                  {module.description}
                </p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto mt-20 w-full max-w-6xl px-6">
        <Card className="flex flex-col items-start justify-between gap-6 lg:flex-row lg:items-center">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-[var(--muted)]">
              Plataforma abierta
            </p>
            <h2 className="mt-3 font-display text-3xl font-semibold text-[var(--foreground)]">
              Prediccion explicable para cuidar mejor, sin reemplazar al experto.
            </h2>
            <p className="mt-2 text-xs text-[var(--muted)]">
              No sustituye la opinion profesional. Es un apoyo para orientar el
              seguimiento.
            </p>
          </div>
          <ButtonLink href="/analyze" size="lg">
            Iniciar analisis
          </ButtonLink>
        </Card>
      </section>

      <Modal
        open={openModal}
        onClose={() => setOpenModal(false)}
        title="Metodologia COCO"
      >
        <p>
          COCO es una plataforma de codigo abierto basada en logica difusa. Toma
          evidencia cientifica, la convierte en variables y reglas explicables, y
          genera un puntaje de riesgo con recomendaciones de seguimiento. Los
          resultados son orientativos y no sustituyen la opinion de un profesional.
        </p>
      </Modal>
    </div>
  );
}
