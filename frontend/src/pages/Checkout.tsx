import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, Check, MapPin } from "lucide-react";
import { ApiError, request } from "@/lib/api";
import type { Address, Cart, Order } from "@/lib/types";
import { money } from "@/lib/format";
import { Button, ButtonLink } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import { EmptyState } from "@/components/EmptyState";
import { ErrorState } from "@/components/ErrorState";
import { useToast } from "@/hooks/toastContext";
import { cn } from "@/lib/cn";

export function Checkout() {
  const navigate = useNavigate();
  const toast = useToast();
  const queryClient = useQueryClient();

  const cart = useQuery({ queryKey: ["cart"], queryFn: () => request<Cart>("/cart") });
  const addresses = useQuery({
    queryKey: ["addresses"],
    queryFn: () => request<Address[]>("/addresses"),
  });

  const [addressId, setAddressId] = useState<number | null>(null);
  const [priceChanged, setPriceChanged] = useState<string | null>(null);

  /**
   * One key per checkout attempt, generated once and kept.
   *
   * This is the whole point of the backend's idempotency support: if the
   * request times out and the customer presses the button again, the same
   * key returns the order the first attempt created instead of placing a
   * second one. A key regenerated on every render would defeat it.
   */
  const idempotencyKey = useMemo(() => crypto.randomUUID(), []);

  const chosen =
    addressId ?? addresses.data?.find((address) => address.is_default)?.id ?? addresses.data?.[0]?.id ?? null;

  const checkout = useMutation({
    mutationFn: (expectedTotal: string) =>
      request<Order>("/orders", {
        method: "POST",
        body: { address_id: chosen, expected_total: expectedTotal },
        idempotencyKey,
      }),
    onSuccess: (order) => {
      queryClient.invalidateQueries({ queryKey: ["cart"] });
      queryClient.invalidateQueries({ queryKey: ["orders"] });
      toast.show("success", `Order #${order.id} placed`);
      navigate(`/orders/${order.id}`);
    },
    onError: async (error: unknown) => {
      if (error instanceof ApiError && error.code === "price_changed") {
        // The server refused because the total moved since the cart was
        // shown. This is the control working, not a failure: re-read the
        // cart, show what it costs now, and make the customer agree again.
        //
        // staleTime: 0 is load-bearing. fetchQuery honours the 30s
        // staleTime set on the query client, so without it this returns
        // the cached cart and the "new total" shown is the old one - which
        // is worse than showing nothing, because the number the customer
        // is asked to confirm would be wrong.
        const fresh = await queryClient.fetchQuery({
          queryKey: ["cart"],
          queryFn: () => request<Cart>("/cart"),
          staleTime: 0,
        });
        setPriceChanged(fresh.total);
        return;
      }
      toast.show("error", error instanceof ApiError ? error.message : "Checkout failed");
    },
  });

  if (cart.isError) return <ErrorState error={cart.error} onRetry={() => cart.refetch()} />;
  if (addresses.isError) return <ErrorState error={addresses.error} onRetry={() => addresses.refetch()} />;

  if (cart.isLoading || addresses.isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-40" />
        <div className="grid gap-6 lg:grid-cols-[1fr_20rem]">
          <Skeleton className="h-64" />
          <Skeleton className="h-48" />
        </div>
      </div>
    );
  }

  if (cart.data!.items.length === 0) {
    return (
      <EmptyState
        icon={<AlertTriangle aria-hidden className="size-5" />}
        title="Your cart is empty"
        description="There is nothing to check out. Add something first."
        action={<ButtonLink to="/">Browse the shop</ButtonLink>}
      />
    );
  }

  if (addresses.data!.length === 0) {
    return (
      <EmptyState
        icon={<MapPin aria-hidden className="size-5" />}
        title="No delivery address yet"
        description="An order needs somewhere to go. Add an address and come back."
        action={<ButtonLink to="/addresses">Add an address</ButtonLink>}
      />
    );
  }

  const total = cart.data!.total;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">Checkout</h1>
        <p className="mt-1 text-sm text-muted">Confirm where this is going and what it costs.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_20rem]">
        <section aria-labelledby="delivery-heading">
          <h2 id="delivery-heading" className="mb-3 text-sm font-semibold text-heading">
            Deliver to
          </h2>
          <div className="space-y-3">
            {addresses.data!.map((address) => {
              const selected = chosen === address.id;
              return (
                <label
                  key={address.id}
                  className={cn(
                    "flex cursor-pointer gap-3 rounded-[--radius-card] border p-4 transition-colors",
                    selected
                      ? "border-brand-500 bg-brand-50/60 dark:bg-brand-700/10"
                      : "border-line bg-surface hover:border-line-strong",
                  )}
                >
                  <input
                    type="radio"
                    name="address"
                    value={address.id}
                    checked={selected}
                    onChange={() => setAddressId(address.id)}
                    className="mt-1 size-4 accent-[oklch(0.54_0.21_275)]"
                  />
                  <div className="min-w-0 text-sm">
                    <p className="font-medium text-heading">
                      {address.recipient_name}
                      {address.label && <span className="ml-2 text-xs text-muted">{address.label}</span>}
                      {address.is_default && (
                        <span className="ml-2 text-xs font-normal text-brand-600 dark:text-brand-300">
                          Default
                        </span>
                      )}
                    </p>
                    <p className="mt-1 text-body">
                      {address.line1}
                      {address.line2 && `, ${address.line2}`}, {address.city}
                      {address.region && `, ${address.region}`}
                      {address.postal_code && ` ${address.postal_code}`}, {address.country}
                    </p>
                    <p className="tabular mt-0.5 text-muted">{address.phone}</p>
                  </div>
                </label>
              );
            })}
          </div>
          <Link to="/addresses" className="mt-3 inline-block text-sm font-medium text-brand-600 hover:underline">
            Manage addresses
          </Link>
        </section>

        <div className="lg:sticky lg:top-24 lg:self-start">
          <Card className="p-5">
            <h2 className="text-sm font-semibold text-heading">Order summary</h2>

            <ul className="mt-4 space-y-2 text-sm">
              {cart.data!.items.map((item) => (
                <li key={item.product_id} className="flex justify-between gap-3">
                  <span className="min-w-0 truncate text-body">
                    {item.name} <span className="tabular text-muted">× {item.quantity}</span>
                  </span>
                  <span className="tabular shrink-0 text-body">{money(item.line_total)}</span>
                </li>
              ))}
            </ul>

            <div className="mt-4 flex justify-between border-t border-line pt-3">
              <span className="font-medium text-heading">Total</span>
              <span className="tabular text-lg font-semibold text-heading">{money(total)}</span>
            </div>

            {priceChanged && (
              <div className="mt-4 rounded-[--radius-control] border border-caution-500/30 bg-caution-50 p-3 text-xs text-caution-700 dark:bg-caution-700/15 dark:text-caution-500">
                <p className="flex gap-2 font-medium">
                  <AlertTriangle aria-hidden className="mt-px size-4 shrink-0" />
                  The price changed before this order went through
                </p>
                <p className="mt-1.5 pl-6">
                  The new total is <strong className="tabular">{money(priceChanged)}</strong>. Nothing has
                  been charged. Confirm below to order at the new price.
                </p>
              </div>
            )}

            <Button
              fullWidth
              size="lg"
              className="mt-5"
              loading={checkout.isPending}
              icon={priceChanged ? <Check aria-hidden className="size-4" /> : undefined}
              onClick={() => {
                setPriceChanged(null);
                checkout.mutate(priceChanged ?? total);
              }}
            >
              {priceChanged ? `Confirm ${money(priceChanged)}` : `Place order`}
            </Button>

            <p className="mt-3 text-xs text-muted">
              Placing the order reserves the stock. Payment is a separate step and nothing is charged
              yet.
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
}
