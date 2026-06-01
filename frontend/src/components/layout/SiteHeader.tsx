import Image from "next/image";
import Link from "next/link";
import { diseases } from "@/lib/diseases";
import { ButtonLink } from "@/components/ui/Button";
import pataImg from "../../../public/pata.png";

export function SiteHeader() {
  return (
    <header className="relative z-20">
      <div className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-6">
        <Link href="/" className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-white/70 shadow-[0_10px_30px_rgba(15,30,30,0.15)]">
            <Image src={pataImg} alt="COCO" width={20} height={20} />
          </span>
          <div>
            <p className="text-sm font-semibold tracking-[0.3em] text-[var(--foreground)]">
              COCO
            </p>
          </div>
        </Link>
        <nav className="hidden items-center gap-6 text-sm font-semibold text-[var(--foreground)] md:flex">
          <Link href="/" prefetch={false}>Inicio</Link>
          <Link href="/analyze" prefetch={false}>Analizar</Link>
          <Link href="/results" prefetch={false}>Resultados</Link>
        </nav>
        <div className="flex items-center gap-3">
          <a
            href="https://github.com/Mamarco13/coco-vet-engine"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Ver repositorio en GitHub"
            className="flex h-9 w-9 items-center justify-center rounded-xl border border-black/10 bg-white/70 text-[var(--foreground)] shadow-[0_4px_12px_rgba(15,30,30,0.08)] transition hover:bg-white hover:shadow-[0_8px_20px_rgba(15,30,30,0.14)]"
          >
            <Image src="/github_logo.png" alt="GitHub" width={18} height={18} />
          </a>
          <ButtonLink href="/analyze" size="sm">
            Analizar perro
          </ButtonLink>
        </div>
      </div>
    </header>
  );
}
