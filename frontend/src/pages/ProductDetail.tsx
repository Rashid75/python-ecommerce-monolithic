import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Minus, Plus, ShoppingCart } from "lucide-react";
import { ApiError, request } from "@/lib/api";
import type { Product } from "@/lib/types";
import { money } from "@/lib/format";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { ProductThumb } from "@/components/ProductThumb";
import { Card } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorState } from "@/components/ErrorState";
import { useToast } from "@/hooks/toastContext";
import { useAuth } from "@/hooks/authContext";

export function ProductDetail() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const toast = useToast();
  const queryClient = useQueryClient();
  const [quantity, setQuantity] = useState(1);

  const product = useQuery({
    queryKey: ["products", id],
    queryFn: () => request<Product>(`/products/${id}`),
  });

  const addToCart = useMutation({
    mutationFn: () =>
      request("/cart/items", {
        method: "POST",
        body: { product_id: Number(id), quantity },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cart"] });
      toast.show("success", `Added ${quantity} × ${product.data!.name} to your cart`);
    },
    onError: (error: unknown) =>
      toast.show("error", error instanceof ApiError ? error.message : "Could not add that item"),
  });

  if (product.isError) return <ErrorState error={product.error} onRetry={() => product.refetch()} />;

  if (product.isLoading) {
    return (
      <div className="grid gap-8 lg:grid-cols-2">
        <Skeleton className="aspect-4/3" />
        <div className="space-y-4">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-9 w-2/3" />
          <Skeleton className="h-6 w-28" />
          <Skeleton className="h-20" />
        </div>
      </div>
    );
  }

  const data = product.data!;
  const soldOut = data.stock_quantity === 0;
  const max = Math.min(data.stock_quantity, 999);

  return (
    <div className="space-y-8">
      <Link
        to="/"
        className="inline-flex items-center gap-1.5 text-sm font-medium text-muted hover:text-heading"
      >
        <ArrowLeft aria-hidden className="size-4" />
        Back to shop
      </Link>

      <div className="grid gap-8 lg:grid-cols-2">
        <ProductThumb product={data} large />

        <div>
          <p className="tabular text-xs uppercase tracking-wide text-muted">{data.sku}</p>
          <h1 className="mt-2 text-2xl font-semibold tracking-tight sm:text-3xl">{data.name}</h1>

          <div className="mt-4 flex flex-wrap items-center gap-3">
            <p className="tabular text-2xl font-semibold text-heading">{money(data.price)}</p>
            {soldOut ? (
              <Badge tone="neutral">Sold out</Badge>
            ) : data.stock_quantity <= 5 ? (
              <Badge tone="caution">Only {data.stock_quantity} left</Badge>
            ) : (
              <Badge tone="positive">In stock</Badge>
            )}
          </div>

          {data.description && (
            <p className="mt-5 text-sm leading-relaxed text-body">{data.description}</p>
          )}

          {!user ? (
            <Card className="mt-8 p-5">
              <p className="text-sm text-body">
                <Link to="/signin" className="font-medium text-brand-600 hover:underline">
                  Sign in
                </Link>{" "}
                to add this to your cart.
              </p>
            </Card>
          ) : (
            <div className="mt-8 flex flex-wrap items-center gap-3">
              <div className="inline-flex items-center rounded-[--radius-control] border border-line">
                <button
                  onClick={() => setQuantity((value) => Math.max(1, value - 1))}
                  disabled={quantity <= 1 || soldOut}
                  aria-label="Decrease quantity"
                  className="inline-flex size-10 items-center justify-center rounded-l-[--radius-control] text-muted transition-colors hover:bg-ink-100 disabled:opacity-40 dark:hover:bg-surface-raised"
                >
                  <Minus aria-hidden className="size-4" />
                </button>
                <span className="tabular w-12 text-center text-sm font-medium text-heading">
                  {quantity}
                </span>
                <button
                  onClick={() => setQuantity((value) => Math.min(max, value + 1))}
                  disabled={quantity >= max || soldOut}
                  aria-label="Increase quantity"
                  className="inline-flex size-10 items-center justify-center rounded-r-[--radius-control] text-muted transition-colors hover:bg-ink-100 disabled:opacity-40 dark:hover:bg-surface-raised"
                >
                  <Plus aria-hidden className="size-4" />
                </button>
              </div>

              <Button
                size="lg"
                disabled={soldOut}
                loading={addToCart.isPending}
                icon={<ShoppingCart aria-hidden className="size-4" />}
                onClick={() => addToCart.mutate()}
              >
                {soldOut ? "Sold out" : "Add to cart"}
              </Button>
            </div>
          )}

          {/* The cart deliberately stores no price, so this number is
              today's and may move before checkout. Saying so once, here,
              is better than a surprise at the last step. */}
          <p className="mt-4 text-xs text-muted">
            The price is confirmed again at checkout before anything is charged.
          </p>
        </div>
      </div>
    </div>
  );
}
