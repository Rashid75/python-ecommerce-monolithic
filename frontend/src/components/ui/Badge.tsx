import type { ReactNode } from "react";
import { cn } from "@/lib/cn";
import type { OrderStatus, PaymentStatus } from "@/lib/types";

type Tone = "neutral" | "positive" | "caution" | "critical" | "brand";

const TONES: Record<Tone, string> = {
  neutral: "bg-ink-100 text-ink-700 dark:bg-surface-raised dark:text-ink-300",
  positive: "bg-positive-50 text-positive-700 dark:bg-positive-700/20 dark:text-positive-500",
  caution: "bg-caution-50 text-caution-700 dark:bg-caution-700/20 dark:text-caution-500",
  critical: "bg-critical-50 text-critical-700 dark:bg-critical-700/20 dark:text-critical-500",
  brand: "bg-brand-50 text-brand-700 dark:bg-brand-700/20 dark:text-brand-300",
};

export function Badge({ tone = "neutral", children }: { tone?: Tone; children: ReactNode }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium capitalize",
        TONES[tone],
      )}
    >
      {children}
    </span>
  );
}

/* Status colours are decided once, here, so an order reads the same on the
 * list page and the detail page. Cancelled is neutral rather than red: it
 * is an ordinary outcome, not a failure, and colouring it as an error
 * makes a customer think something went wrong. */
const ORDER_TONES: Record<OrderStatus, Tone> = {
  pending: "caution",
  paid: "brand",
  shipped: "brand",
  delivered: "positive",
  cancelled: "neutral",
};

export function OrderStatusBadge({ status }: { status: OrderStatus }) {
  return <Badge tone={ORDER_TONES[status]}>{status}</Badge>;
}

const PAYMENT_TONES: Record<PaymentStatus, Tone> = {
  pending: "caution",
  succeeded: "positive",
  failed: "critical",
  refunded: "neutral",
};

export function PaymentStatusBadge({ status }: { status: PaymentStatus }) {
  return <Badge tone={PAYMENT_TONES[status]}>{status}</Badge>;
}
