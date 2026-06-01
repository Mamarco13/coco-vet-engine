import { cn } from "@/lib/utils";

type ProgressBarProps = {
  value: number;
  max?: number;
  className?: string;
  indicatorClassName?: string;
};

export function ProgressBar({
  value,
  max = 100,
  className,
  indicatorClassName,
}: ProgressBarProps) {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));

  return (
    <div className={cn("h-2 w-full overflow-hidden rounded-full bg-black/10", className)}>
      <div
        className={cn(
          "h-full rounded-full bg-[var(--accent)] transition-all duration-300",
          indicatorClassName
        )}
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
}
