import Image from "next/image";
import Link from "next/link";
import { diseases } from "@/lib/diseases";
import { ButtonLink } from "@/components/ui/Button";

export function SiteHeader() {
  return (
    <header className="relative z-20">
      <div className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-6">
        <Link href="/" className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-white/70 shadow-[0_10px_30px_rgba(15,30,30,0.15)]">
            <Image src="/pata.png" alt="COCO" width={20} height={20} />
          </span>
          <div>
            <p className="text-sm font-semibold tracking-[0.3em] text-[var(--foreground)]">
              COCO
            </p>
          </div>
        </Link>
        <nav className="hidden items-center gap-6 text-sm font-semibold text-[var(--foreground)] md:flex">
          <Link href="/">Inicio</Link>
          <Link href="/analyze">Analizar</Link>
          <Link href="/results">Resultados</Link>
        </nav>
        <div className="flex items-center gap-3">
          <ButtonLink href="/analyze" size="sm">
            Analizar perro
          </ButtonLink>
        </div>
      </div>
    </header>
  );
}
