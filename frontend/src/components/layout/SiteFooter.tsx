import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="border-t border-white/60 bg-white/40">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-6 py-10 text-sm text-[var(--muted)] md:flex-row md:items-center md:justify-between">
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-[0.3em] text-[var(--foreground)]">
            COCO
          </p>
          <p>Deteccion temprana con apoyo de AI veterinaria.</p>
          <p className="text-xs">
            Esta herramienta no sustituye la evaluacion de un veterinario.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-4 text-xs font-semibold uppercase tracking-[0.2em]">
          <Link href="/" prefetch={false}>Inicio</Link>
          <Link href="/analyze" prefetch={false}>Analizar</Link>
          <Link href="/results" prefetch={false}>Resultados</Link>
        </div>
      </div>
    </footer>
  );
}
