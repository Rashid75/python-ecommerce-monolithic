import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Package } from "lucide-react";
import { request } from "@/lib/api";
import type { Order } from "@/lib/types";
import { dateTime, money } from "@/lib/format";
import { OrderStatusBadge } from "@/components/ui/Badge";
import { ButtonLink } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import { EmptyState } from "@/components/EmptyState";
import { ErrorState } from "@/components/ErrorState";

export function Orders() {
  const orders = useQuery({ queryKey: ["orders"], queryFn: () => request<Order[]>("/orders") });

  if (orders.isError) return <ErrorState error={orders.error} onRetry={() => orders.refetch()} />;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">Orders</h1>
        <p className="mt-1 text-sm text-muted">Everything you have placed, newest first.</p>
      </div>

      {orders.isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }, (_, index) => (
            <Skeleton key={index} className="h-24" />
          ))}
        </div>
      ) : orders.data!.length === 0 ? (
        <EmptyState
          icon={<Package aria-hidden className="size-5" />}
          title="No orders yet"
          description="When you place an order it will appear here, with everything it contained at the price you paid."
          action={<ButtonLink to="/">Start shopping</ButtonLink>}
        />
      ) : (
        <ul className="space-y-3">
          {orders.data!.map((order) => (
            <li key={order.id}>
              <Link
                to={`/orders/${order.id}`}
                className="block rounded-[--radius-card] transition-shadow hover:shadow-raised"
              >
                <Card className="flex flex-wrap items-center gap-x-6 gap-y-3 p-5">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-3">
                      <p className="tabular font-semibold text-heading">Order #{order.id}</p>
                      <OrderStatusBadge status={order.status} />
                    </div>
                    <p className="mt-1 text-sm text-muted">
                      {dateTime(order.created_at)} · {order.items.length}{" "}
                      {order.items.length === 1 ? "item" : "items"}
                    </p>
                  </div>
                  <p className="tabular text-lg font-semibold text-heading">
                    {money(order.total_amount)}
                  </p>
                </Card>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
