import { forwardRef, useId, type InputHTMLAttributes, type ReactNode } from "react";
import { cn } from "@/lib/cn";

type Props = InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  error?: string;
  hint?: ReactNode;
};

/**
 * A labelled input.
 *
 * The label is always rendered and always tied to the input by id - never
 * a placeholder standing in for one. A placeholder disappears the moment
 * someone types, which leaves a form of unlabelled boxes for anyone who
 * looks away mid-task, and nothing at all for a screen reader.
 */
export const Field = forwardRef<HTMLInputElement, Props>(function Field(
  { label, error, hint, className, id, required, ...rest },
  ref,
) {
  const generated = useId();
  const inputId = id ?? generated;
  const errorId = `${inputId}-error`;
  const hintId = `${inputId}-hint`;

  return (
    <div className="space-y-1.5">
      <label htmlFor={inputId} className="block text-sm font-medium text-heading">
        {label}
        {required && (
          <span aria-hidden className="ml-0.5 text-critical-500">
            *
          </span>
        )}
      </label>
      <input
        ref={ref}
        id={inputId}
        required={required}
        aria-invalid={error ? true : undefined}
        // Points the screen reader at the message, so an error is announced
        // rather than only coloured red.
        aria-describedby={cn(error && errorId, hint && hintId) || undefined}
        className={cn(
          "block w-full rounded-[--radius-control] border bg-surface px-3 py-2 text-sm text-heading",
          "placeholder:text-muted shadow-subtle transition-colors",
          "disabled:cursor-not-allowed disabled:opacity-60",
          error ? "border-critical-500" : "border-line hover:border-line-strong",
          className,
        )}
        {...rest}
      />
      {hint && !error && (
        <p id={hintId} className="text-xs text-muted">
          {hint}
        </p>
      )}
      {error && (
        <p id={errorId} className="text-xs font-medium text-critical-600">
          {error}
        </p>
      )}
    </div>
  );
});
