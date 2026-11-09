import { Link, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, CreditCard, Receipt, XCircle } from "lucide-react";
import { ApiError, request } from "@/lib/api";
import type { Order, Payment, PaymentStarted } from "@/lib/types";
import { dateTime, money } from "@/lib/format";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { OrderStatusBadge, PaymentStatusBadge } from "@/components/ui/Badge";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorState } from "@/components/ErrorState";
import { useToast } from "@/hooks/toastContext";

export function OrderDetail() {
  const { id } = useParams<{ id: string }>();
  const toast = useToast();
  const queryClient = useQueryClient();

  const order = useQuery({
    queryKey: ["orders", id],
    queryFn: () => request<Order>(`/orders/${id}`),
  });

  const payments = useQuery({
    queryKey: ["orders", id, "payments"],
    queryFn: () => request<Payment[]>(`/orders/${id}/payments`),
    enabled: Boolean(order.data),
  });

  const refresh = () => {
    queryClient.invalidateQueries({ queryKey: ["orders"] });
    queryClient.invalidateQueries({ queryKey: ["orders", id, "payments"] });
  };

  const cancel = useMutation({
    mutationFn: () => request<Order>(`/orders/${id}/cancellation`, { method: "POST" }),
    onSuccess: () => {
      refresh();
      toast.show("info", "Order cancelled and the stock returned");
    },
    onError: (error: unknown) =>
      toast.show("error", error instanceof ApiError ? error.message : "Could not cancel that"),
  });

  const pay = useMutation({
    mutationFn: () => request<PaymentStarted>(`/orders/${id}/payments`, { method: "POST" }),
    onSuccess: (payment) => {
      refresh();
      // Honest wording. Starting a payment creates a pending record; the
      // order only becomes paid when the provider confirms by webhook, and
      // telling the customer otherwise would be a lie the UI cannot keep.
      toast.show("info", `Payment started for ${money(payment.amount, payment.currency)}. Awaiting the provider.`);
    },
    onError: (error: unknown) =>
      toast.show("error", error instanceof ApiError ? error.message : "Could not start a payment"),
  });

  if (order.isError) return <ErrorState error={order.error} onRetry={() => order.refetch()} />;

  if (order.isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-48" />
        <div className="grid gap-6 lg:grid-cols-[1fr_20rem]">
          <Skeleton className="h-72" />
          <Skeleton className="h-56" />
        </div>
      </div>
    );
  }

  const data = order.data!;
  const cancellable = data.status === "pending";
  const payable = data.status === "pending";

  return (
    <div className="space-y-8">
      <div>
        <Link
          to="/orders"
          className="inline-flex items-center gap-1.5 text-sm font-medium text-muted hover:text-heading"
        >
          <ArrowLeft aria-hidden className="size-4" />
          All orders
        </Link>

        <div className="mt-3 flex flex-wrap items-center gap-3">
          <h1 className="tabular text-2xl font-semibold tracking-tight sm:text-3xl">
            Order #{data.id}
          </h1>
          <OrderStatusBadge status={data.status} />
        </div>
        <p className="mt-1 text-sm text-muted">Placed {dateTime(data.created_at)}</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_20rem]">
        <div className="space-y-6">
          <section aria-labelledby="items-heading">
            <h2 id="items-heading" className="mb-3 text-sm font-semibold text-heading">
              Items
            </h2>
            <Card className="px-5">
              <ul className="divide-y divide-line">
                {data.items.map((item) => (
                  <li key={item.product_id} className="flex flex-wrap items-baseline gap-x-4 gap-y-1 py-4">
                    <div className="min-w-0 flex-1">
                      <Link
                        to={`/products/${item.product_id}`}
                        className="text-sm font-medium text-heading hover:text-brand-600"
                      >
                        {item.name}
                      </Link>
                      <p className="tabular mt-0.5 text-xs uppercase tracking-wide text-muted">
                        {item.sku}
                      </p>
                    </div>
                    <p className="tabular text-sm text-muted">
                      {money(item.unit_price)} × {item.quantity}
                    </p>
                    <p className="tabular w-24 text-right text-sm font-semibold text-heading">
                      {money(item.line_total)}
                    </p>
                  </li>
                ))}
              </ul>
            </Card>
            {/* The record, stated plainly. These are copies taken at
                checkout, which is why they can differ from the catalogue. */}
            <p className="mt-2 text-xs text-muted">
              Names and prices are as they were when you ordered, not as they are now.
            </p>
          </section>

          <section aria-labelledby="payments-heading">
            <h2 id="payments-heading" className="mb-3 text-sm font-semibold text-heading">
              Payments
            </h2>
            {payments.isLoading ? (
              <Skeleton className="h-20" />
            ) : payments.data && payments.data.length > 0 ? (
              <Card className="px-5">
                <ul className="divide-y divide-line">
                  {payments.data.map((payment) => (
                    <li key={payment.id} className="flex flex-wrap items-center gap-x-4 gap-y-2 py-4">
                      <div className="flex-1">
                        <p className="tabular text-sm font-medium text-heading">
                          {money(payment.amount, payment.currency)}
                        </p>
                        <p className="mt-0.5 text-xs text-muted">{dateTime(payment.created_at)}</p>
                      </div>
                      <PaymentStatusBadge status={payment.status} />
                    </li>
                  ))}
                </ul>
              </Card>
            ) : (
              <Card className="p-5">
                <p className="text-sm text-muted">No payment attempts yet.</p>
              </Card>
            )}
          </section>
        </div>

        <div className="space-y-6 lg:sticky lg:top-24 lg:self-start">
          <Card className="p-5">
            <h2 className="text-sm font-semibold text-heading">Total</h2>
            <p className="tabular mt-2 text-2xl font-semibold text-heading">
              {money(data.total_amount)}
            </p>

            {payable && (
              <Button
                fullWidth
                className="mt-4"
                loading={pay.isPending}
                icon={<CreditCard aria-hidden className="size-4" />}
                onClick={() => pay.mutate()}
              >
                Pay now
              </Button>
            )}

            {cancellable && (
              <Button
                variant="secondary"
                fullWidth
                className="mt-2"
                loading={cancel.isPending}
                icon={<XCircle aria-hidden className="size-4" />}
                onClick={() => cancel.mutate()}
              >
                Cancel order
              </Button>
            )}

            {data.status === "paid" && (
              <p className="mt-3 flex gap-2 text-xs text-muted">
                <Receipt aria-hidden className="mt-px size-3.5 shrink-0" />
                Paid. Cancelling now is a refund, which the shop arranges.
              </p>
            )}
          </Card>

          <Card className="p-5">
            <h2 className="text-sm font-semibold text-heading">Delivering to</h2>
            <address className="mt-2 text-sm not-italic text-body">
              <p className="font-medium text-heading">{data.shipping.recipient_name}</p>
              <p className="mt-1">{data.shipping.line1}</p>
              {data.shipping.line2 && <p>{data.shipping.line2}</p>}
              <p>
                {data.shipping.city}
                {data.shipping.region && `, ${data.shipping.region}`}
                {data.shipping.postal_code && ` ${data.shipping.postal_code}`}
              </p>
              <p>{data.shipping.country}</p>
              <p className="tabular mt-1 text-muted">{data.shipping.phone}</p>
            </address>
          </Card>
        </div>
      </div>

    </div>
  );
}
