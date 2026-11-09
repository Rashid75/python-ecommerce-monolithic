import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, Minus, Plus, ShoppingCart, Trash2 } from "lucide-react";
import { ApiError, request } from "@/lib/api";
import type { Cart, CartItem } from "@/lib/types";
import { money } from "@/lib/format";
import { Button, ButtonLink } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import { EmptyState } from "@/components/EmptyState";
import { ErrorState } from "@/components/ErrorState";
import { useToast } from "@/hooks/toastContext";

const ISSUE_TEXT: Record<string, string> = {
  unavailable: "No longer on sale",
  insufficient_stock: "Not enough stock left",
};

function Line({ item }: { item: CartItem }) {
  const toast = useToast();
  const queryClient = useQueryClient();

  const onError = (error: unknown) =>
    toast.show("error", error instanceof ApiError ? error.message : "That did not work");
  const onSuccess = () => queryClient.invalidateQueries({ queryKey: ["cart"] });

  const setQuantity = useMutation({
    mutationFn: (quantity: number) =>
      request(`/cart/items/${item.product_id}`, { method: "PUT", body: { quantity } }),
    onSuccess,
    onError,
  });

  const remove = useMutation({
    mutationFn: () => request(`/cart/items/${item.product_id}`, { method: "DELETE" }),
    onSuccess: () => {
      onSuccess();
      toast.show("info", `${item.name} removed`);
    },
    onError,
  });

  const busy = setQuantity.isPending || remove.isPending;

  return (
    <li className="flex gap-4 py-5">
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-start justify-between gap-x-4 gap-y-1">
          <div className="min-w-0">
            <Link
              to={`/products/${item.product_id}`}
              className="text-sm font-medium text-heading hover:text-brand-600"
            >
              {item.name}
            </Link>
            <p className="tabular mt-0.5 text-xs uppercase tracking-wide text-muted">{item.sku}</p>
          </div>
          <p className="tabular text-sm font-semibold text-heading">{money(item.line_total)}</p>
        </div>

        {item.issue && (
          <p className="mt-2 inline-flex items-center gap-1.5 rounded-md bg-caution-50 px-2 py-1 text-xs font-medium text-caution-700 dark:bg-caution-700/15 dark:text-caution-500">
            <AlertTriangle aria-hidden className="size-3.5" />
            {ISSUE_TEXT[item.issue] ?? item.issue}
            {item.issue === "insufficient_stock" && ` — ${item.available_stock} available`}
          </p>
        )}

        <div className="mt-3 flex items-center justify-between gap-4">
          <div className="inline-flex items-center rounded-[--radius-control] border border-line">
            <button
              onClick={() => setQuantity.mutate(item.quantity - 1)}
              disabled={busy || item.quantity <= 1}
              aria-label={`Decrease quantity of ${item.name}`}
              className="inline-flex size-8 items-center justify-center rounded-l-[--radius-control] text-muted transition-colors hover:bg-ink-100 disabled:opacity-40 dark:hover:bg-surface-raised"
            >
              <Minus aria-hidden className="size-3.5" />
            </button>
            <span className="tabular w-10 text-center text-sm font-medium text-heading" aria-live="polite">
              {item.quantity}
            </span>
            <button
              onClick={() => setQuantity.mutate(item.quantity + 1)}
              disabled={busy || item.quantity >= 999}
              aria-label={`Increase quantity of ${item.name}`}
              className="inline-flex size-8 items-center justify-center rounded-r-[--radius-control] text-muted transition-colors hover:bg-ink-100 disabled:opacity-40 dark:hover:bg-surface-raised"
            >
              <Plus aria-hidden className="size-3.5" />
            </button>
          </div>

          <div className="flex items-center gap-3">
            <span className="tabular text-xs text-muted">{money(item.unit_price)} each</span>
            <button
              onClick={() => remove.mutate()}
              disabled={busy}
              aria-label={`Remove ${item.name}`}
              className="inline-flex size-8 items-center justify-center rounded-[--radius-control] text-muted transition-colors hover:bg-critical-50 hover:text-critical-600 dark:hover:bg-critical-700/15"
            >
              <Trash2 aria-hidden className="size-4" />
            </button>
          </div>
        </div>
      </div>
    </li>
  );
}

export function CartPage() {
  const toast = useToast();
  const queryClient = useQueryClient();
  const cart = useQuery({ queryKey: ["cart"], queryFn: () => request<Cart>("/cart") });

  const clear = useMutation({
    mutationFn: () => request("/cart", { method: "DELETE" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cart"] });
      toast.show("info", "Cart emptied");
    },
  });

  if (cart.isError) return <ErrorState error={cart.error} onRetry={() => cart.refetch()} />;

  if (cart.isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-32" />
        <Card className="divide-y divide-line px-5">
          {Array.from({ length: 3 }, (_, index) => (
            <div key={index} className="space-y-3 py-5">
              <Skeleton className="h-4 w-1/3" />
              <Skeleton className="h-8 w-40" />
            </div>
          ))}
        </Card>
      </div>
    );
  }

  const data = cart.data!;

  if (data.items.length === 0) {
    return (
      <div className="space-y-8">
        <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">Your cart</h1>
        <EmptyState
          icon={<ShoppingCart aria-hidden className="size-5" />}
          title="Your cart is empty"
          description="Browse the catalogue and add something to get started."
          action={<ButtonLink to="/">Start shopping</ButtonLink>}
        />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">Your cart</h1>
        <Button variant="ghost" size="sm" onClick={() => clear.mutate()} loading={clear.isPending}>
          Empty cart
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_20rem]">
        <Card className="px-5">
          <ul className="divide-y divide-line">
            {data.items.map((item) => (
              <Line key={item.product_id} item={item} />
            ))}
          </ul>
        </Card>

        <div className="lg:sticky lg:top-24 lg:self-start">
          <Card className="p-5">
            <h2 className="text-sm font-semibold text-heading">Summary</h2>

            <dl className="mt-4 space-y-2 text-sm">
              <div className="flex justify-between">
                <dt className="text-muted">Items</dt>
                <dd className="tabular text-body">{data.total_items}</dd>
              </div>
              <div className="flex justify-between border-t border-line pt-3">
                <dt className="font-medium text-heading">Total</dt>
                <dd className="tabular text-lg font-semibold text-heading">{money(data.total)}</dd>
              </div>
            </dl>

            {data.has_issues && (
              <p className="mt-4 flex gap-2 rounded-[--radius-control] bg-caution-50 p-3 text-xs text-caution-700 dark:bg-caution-700/15 dark:text-caution-500">
                <AlertTriangle aria-hidden className="mt-px size-4 shrink-0" />
                Some items cannot be bought right now. Fix those lines before checking out.
              </p>
            )}

            {/* Prices are read live on every request, so this total is
                today's. Checkout sends it back and the server refuses if it
                has moved - saying so here means the refusal is expected
                rather than alarming. */}
            <p className="mt-4 text-xs text-muted">
              Prices are checked again at checkout. If one has changed you will be shown the new
              total before anything is charged.
            </p>

            {data.has_issues ? (
              <Button fullWidth className="mt-5" disabled>
                Checkout
              </Button>
            ) : (
              <ButtonLink fullWidth className="mt-5" to="/checkout">
                Checkout
              </ButtonLink>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}
