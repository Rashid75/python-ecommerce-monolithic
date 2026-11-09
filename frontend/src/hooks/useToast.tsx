import { useCallback, useMemo, useState, type ReactNode } from "react";
import { CheckCircle2, AlertTriangle, Info, X } from "lucide-react";
import { cn } from "@/lib/cn";
import { ToastContext, type ToastTone } from "@/hooks/toastContext";

type Tone = ToastTone;
type Toast = { id: number; tone: Tone; message: string };


const ICONS: Record<Tone, typeof CheckCircle2> = {
  success: CheckCircle2,
  error: AlertTriangle,
  info: Info,
};

const TONES: Record<Tone, string> = {
  success: "border-positive-500/30 bg-positive-50 text-positive-700 dark:bg-positive-700/15 dark:text-positive-500",
  error: "border-critical-500/30 bg-critical-50 text-critical-700 dark:bg-critical-700/15 dark:text-critical-500",
  info: "border-brand-500/30 bg-brand-50 text-brand-700 dark:bg-brand-700/15 dark:text-brand-300",
};

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const dismiss = useCallback((id: number) => {
    setToasts((current) => current.filter((toast) => toast.id !== id));
  }, []);

  const show = useCallback(
    (tone: Tone, message: string) => {
      const id = Date.now() + Math.random();
      setToasts((current) => [...current, { id, tone, message }]);
      // Errors stay longer: they usually say something the customer has to
      // read and act on, while a success is a confirmation they expected.
      window.setTimeout(() => dismiss(id), tone === "error" ? 7000 : 4000);
    },
    [dismiss],
  );

  const value = useMemo(() => ({ show }), [show]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      {/* aria-live so a screen reader announces the message. "polite"
          rather than "assertive": it should not interrupt what someone is
          already reading. */}
      <div
        aria-live="polite"
        aria-atomic="false"
        className="pointer-events-none fixed inset-x-4 bottom-4 z-50 flex flex-col items-center gap-2 sm:inset-x-auto sm:right-6 sm:items-end"
      >
        {toasts.map((toast) => {
          const Icon = ICONS[toast.tone];
          return (
            <div
              key={toast.id}
              role="status"
              className={cn(
                "pointer-events-auto flex w-full max-w-sm items-start gap-3 rounded-[--radius-card] border px-4 py-3 shadow-floating",
                "animate-[fade-in_150ms_ease-out]",
                TONES[toast.tone],
              )}
            >
              <Icon aria-hidden className="mt-0.5 size-4 shrink-0" />
              <p className="flex-1 text-sm font-medium">{toast.message}</p>
              <button
                onClick={() => dismiss(toast.id)}
                aria-label="Dismiss notification"
                className="shrink-0 rounded opacity-60 transition-opacity hover:opacity-100"
              >
                <X aria-hidden className="size-4" />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
}
