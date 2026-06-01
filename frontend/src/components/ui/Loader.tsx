import { cn } from "@/lib/utils";

type LoaderProps = {
  label?: string;
  className?: string;
};

export function Loader({ label = "Cargando", className }: LoaderProps) {
  return (
    <div className={cn("flex items-center gap-3 text-sm text-[var(--muted)]", className)}>
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-black/30 border-t-transparent" />
      <span>{label}</span>
    </div>
  );
}
