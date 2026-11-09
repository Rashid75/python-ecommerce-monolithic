import { forwardRef, type AnchorHTMLAttributes, type ButtonHTMLAttributes, type ReactNode } from "react";
import { Link, type LinkProps } from "react-router-dom";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/cn";

/**
 * The only button in the application.
 *
 * Variants are a fixed list rather than free-form classes, because "which
 * blue is the primary button" is a question an interface should only be
 * able to answer one way.
 */
type Variant = "primary" | "secondary" | "ghost" | "danger";
type Size = "sm" | "md" | "lg";

const VARIANTS: Record<Variant, string> = {
  primary:
    "bg-brand-600 text-white shadow-subtle hover:bg-brand-700 active:bg-brand-800 disabled:hover:bg-brand-600",
  secondary:
    "bg-surface text-heading border border-line shadow-subtle hover:bg-ink-50 hover:border-line-strong dark:hover:bg-surface-raised",
  ghost: "text-body hover:bg-ink-100 dark:hover:bg-surface-raised",
  danger: "bg-critical-600 text-white shadow-subtle hover:bg-critical-700 active:bg-critical-700",
};

const SIZES: Record<Size, string> = {
  sm: "h-8 px-3 text-sm gap-1.5",
  md: "h-10 px-4 text-sm gap-2",
  lg: "h-12 px-6 text-base gap-2",
};

function buttonClasses(variant: Variant, size: Size, fullWidth?: boolean, className?: string) {
  return cn(
    "inline-flex items-center justify-center rounded-[--radius-control] font-medium",
    "transition-colors duration-150",
    "disabled:cursor-not-allowed disabled:opacity-55",
    VARIANTS[variant],
    SIZES[size],
    fullWidth && "w-full",
    className,
  );
}

type Shared = {
  variant?: Variant;
  size?: Size;
  fullWidth?: boolean;
  icon?: ReactNode;
};

type Props = ButtonHTMLAttributes<HTMLButtonElement> & Shared & { loading?: boolean };

export const Button = forwardRef<HTMLButtonElement, Props>(function Button(
  { variant = "primary", size = "md", loading = false, icon, fullWidth, className, children, disabled, ...rest },
  ref,
) {
  return (
    <button
      ref={ref}
      // A loading button is disabled, so a double click cannot submit
      // twice. The backend's idempotency key is the real protection; this
      // is the half that stops the user wondering whether it worked.
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      className={buttonClasses(variant, size, fullWidth, className)}
      {...rest}
    >
      {loading ? <Loader2 aria-hidden className="size-4 animate-spin" /> : icon}
      {children}
    </button>
  );
});

/**
 * A link that looks like a button.
 *
 * Separate from Button on purpose. "Go somewhere" is an anchor and must
 * behave like one - middle-click, open in new tab, copy address - and
 * putting a Link inside a <button> produces invalid HTML that does none of
 * that. Same styles, right element.
 */
type LinkButtonProps = LinkProps & AnchorHTMLAttributes<HTMLAnchorElement> & Shared;

export function ButtonLink({
  variant = "primary",
  size = "md",
  icon,
  fullWidth,
  className,
  children,
  ...rest
}: LinkButtonProps) {
  return (
    <Link className={buttonClasses(variant, size, fullWidth, className)} {...rest}>
      {icon}
      {children}
    </Link>
  );
}
