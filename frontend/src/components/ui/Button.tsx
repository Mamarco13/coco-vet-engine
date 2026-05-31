import Link from "next/link";
import type { ButtonHTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils";

type ButtonVariant = "primary" | "secondary" | "outline" | "ghost";

type ButtonSize = "sm" | "md" | "lg";

type BaseProps = {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  className?: string;
  children: ReactNode;
};

type ButtonProps = BaseProps &
  ButtonHTMLAttributes<HTMLButtonElement> & {
    href?: never;
  };

type ButtonLinkProps = BaseProps & {
  href: string;
  target?: string;
  rel?: string;
  prefetch?: boolean;
};

const baseStyles =
  "inline-flex items-center justify-center gap-2 rounded-full font-semibold transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-black/40 disabled:opacity-50 disabled:pointer-events-none";

const variantStyles: Record<ButtonVariant, string> = {
  primary:
    "bg-[var(--accent)] text-white shadow-[0_18px_40px_rgba(13,139,141,0.35)] hover:translate-y-[-1px]",
  secondary:
    "bg-white/70 text-[var(--foreground)] border border-black/5 shadow-[0_10px_30px_rgba(10,20,20,0.08)] hover:bg-white",
  outline:
    "border border-black/10 text-[var(--foreground)] hover:bg-black/5",
  ghost: "text-[var(--foreground)] hover:bg-black/5",
};

const sizeStyles: Record<ButtonSize, string> = {
  sm: "h-9 px-4 text-sm",
  md: "h-11 px-5 text-sm",
  lg: "h-12 px-6 text-base",
};

function ButtonContent({ isLoading, children }: Pick<BaseProps, "isLoading" | "children">) {
  return (
    <>
      {isLoading && (
        <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/70 border-t-transparent" />
      )}
      <span>{children}</span>
    </>
  );
}

export function Button({
  variant = "primary",
  size = "md",
  isLoading,
  className,
  children,
  type,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(baseStyles, variantStyles[variant], sizeStyles[size], className)}
      aria-busy={isLoading || undefined}
      type={type ?? "button"}
      {...props}
    >
      <ButtonContent isLoading={isLoading}>{children}</ButtonContent>
    </button>
  );
}

export function ButtonLink({
  variant = "primary",
  size = "md",
  isLoading,
  className,
  children,
  href,
  target,
  rel,
  prefetch = false,
}: ButtonLinkProps) {
  return (
    <Link
      href={href}
      target={target}
      rel={rel}
      prefetch={prefetch}
      className={cn(baseStyles, variantStyles[variant], sizeStyles[size], className)}
      aria-busy={isLoading || undefined}
    >
      <ButtonContent isLoading={isLoading}>{children}</ButtonContent>
    </Link>
  );
}
