import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

type CardProps = {
  className?: string;
  children: ReactNode;
};

export function Card({ className, children }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-3xl border border-white/50 bg-white/70 p-6 shadow-[0_20px_60px_rgba(15,30,30,0.12)] backdrop-blur-xl",
        className
      )}
    >
      {children}
    </div>
  );
}
