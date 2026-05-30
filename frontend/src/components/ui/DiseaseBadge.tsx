import { cn } from "@/lib/utils";

type DiseaseBadgeProps = {
  label: string;
  className?: string;
};

export function DiseaseBadge({ label, className }: DiseaseBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border border-black/10 bg-white/70 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-[var(--foreground)]",
        className
      )}
    >
      {label}
    </span>
  );
}
