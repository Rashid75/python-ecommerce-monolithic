import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { PackageSearch, Plus, Search, SlidersHorizontal } from "lucide-react";
import { request, ApiError } from "@/lib/api";
import type { Category, Page, Product } from "@/lib/types";
import { money } from "@/lib/format";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import { ProductThumb } from "@/components/ProductThumb";
import { EmptyState } from "@/components/EmptyState";
import { ErrorState } from "@/components/ErrorState";
import { useToast } from "@/hooks/toastContext";
import { useAuth } from "@/hooks/authContext";
import { cn } from "@/lib/cn";

const PER_PAGE = 12;

function ProductCardSkeleton() {
  return (
    <Card className="overflow-hidden">
      <Skeleton className="aspect-4/3 rounded-none" />
      <div className="space-y-3 p-4">
        <Skeleton className="h-3 w-16" />
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-5 w-20" />
      </div>
    </Card>
  );
}

function ProductCard({ product }: { product: Product }) {
  const { user } = useAuth();
  const toast = useToast();
  const queryClient = useQueryClient();

  const addToCart = useMutation({
    mutationFn: () =>
      request("/cart/items", { method: "POST", body: { product_id: product.id, quantity: 1 } }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cart"] });
      toast.show("success", `${product.name} added to your cart`);
    },
    onError: (error: unknown) => {
      toast.show("error", error instanceof ApiError ? error.message : "Could not add that item");
    },
  });

  const soldOut = product.stock_quantity === 0;

  return (
    <Card className="group flex flex-col overflow-hidden transition-shadow hover:shadow-raised">
      <Link to={`/products/${product.id}`} className="relative block">
        <ProductThumb product={product} />
        {soldOut && (
          <div className="absolute inset-0 flex items-center justify-center bg-ink-950/55">
            <Badge tone="neutral">Sold out</Badge>
          </div>
        )}
      </Link>

      <div className="flex flex-1 flex-col p-4">
        <p className="tabular text-xs uppercase tracking-wide text-muted">{product.sku}</p>
        <h3 className="mt-1 text-sm font-medium leading-snug text-heading">
          <Link to={`/products/${product.id}`} className="hover:text-brand-600">
            {product.name}
          </Link>
        </h3>

        <div className="mt-auto pt-3">
          <p className="tabular text-lg font-semibold text-heading">{money(product.price)}</p>
          {/* Reserves the line whether or not there is a warning, so cards
              in a row keep the same height and their buttons stay aligned. */}
          <p className="mt-0.5 h-4 text-xs font-medium text-caution-700 dark:text-caution-500">
            {!soldOut && product.stock_quantity <= 5
              ? `Only ${product.stock_quantity} left`
              : " "}
          </p>
        </div>

        {user && (
          <Button
            size="sm"
            className="mt-4"
            fullWidth
            disabled={soldOut}
            loading={addToCart.isPending}
            icon={<Plus aria-hidden className="size-4" />}
            onClick={() => addToCart.mutate()}
          >
            {soldOut ? "Sold out" : "Add to cart"}
          </Button>
        )}
      </div>
    </Card>
  );
}

export function Products() {
  const [params, setParams] = useSearchParams();
  const page = Number(params.get("page") ?? 1);
  const search = params.get("search") ?? "";
  const categoryId = params.get("category") ?? "";
  const inStock = params.get("in_stock") === "true";

  // Typing in the box updates this immediately; the query waits. Without
  // the delay every keystroke is a request, and the results flicker
  // through partial matches of a word nobody finished typing.
  const [draft, setDraft] = useState(search);
  useEffect(() => setDraft(search), [search]);
  useEffect(() => {
    const timer = window.setTimeout(() => {
      if (draft === search) return;
      const next = new URLSearchParams(params);
      if (draft) next.set("search", draft);
      else next.delete("search");
      next.delete("page");
      setParams(next, { replace: true });
    }, 300);
    return () => window.clearTimeout(timer);
  }, [draft, search, params, setParams]);

  const query = new URLSearchParams({
    limit: String(PER_PAGE),
    offset: String((page - 1) * PER_PAGE),
    is_active: "true",
  });
  if (search) query.set("search", search);
  if (categoryId) query.set("category_id", categoryId);
  if (inStock) query.set("in_stock", "true");

  const products = useQuery({
    queryKey: ["products", query.toString()],
    queryFn: () => request<Page<Product>>(`/products?${query.toString()}`),
    // Keeps the previous page on screen while the next loads, so paging
    // does not blank the grid and collapse the page height.
    placeholderData: keepPreviousData,
  });

  const categories = useQuery({
    queryKey: ["categories"],
    queryFn: () => request<Page<Category>>("/categories?limit=100"),
  });

  function setParam(key: string, value: string | null) {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value);
    else next.delete(key);
    next.delete("page");
    setParams(next);
  }

  const total = products.data?.total ?? 0;
  const pageCount = Math.max(1, Math.ceil(total / PER_PAGE));

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">Shop</h1>
        <p className="mt-1 text-sm text-muted">
          {products.isLoading ? "Loading the catalogue…" : `${total} ${total === 1 ? "product" : "products"}`}
        </p>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <Search aria-hidden className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted" />
          <input
            type="search"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder="Search by name or SKU"
            aria-label="Search products"
            className="h-10 w-full rounded-[--radius-control] border border-line bg-surface pl-9 pr-3 text-sm text-heading shadow-subtle placeholder:text-muted hover:border-line-strong"
          />
        </div>

        <div className="flex items-center gap-2">
          <SlidersHorizontal aria-hidden className="size-4 shrink-0 text-muted" />
          <select
            value={categoryId}
            onChange={(event) => setParam("category", event.target.value || null)}
            aria-label="Filter by category"
            className="h-10 rounded-[--radius-control] border border-line bg-surface px-3 text-sm text-heading shadow-subtle hover:border-line-strong"
          >
            <option value="">All categories</option>
            {categories.data?.items.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>

          <button
            onClick={() => setParam("in_stock", inStock ? null : "true")}
            aria-pressed={inStock}
            className={cn(
              "h-10 rounded-[--radius-control] border px-3 text-sm font-medium shadow-subtle transition-colors",
              inStock
                ? "border-brand-500 bg-brand-50 text-brand-700 dark:bg-brand-700/20 dark:text-brand-300"
                : "border-line bg-surface text-body hover:border-line-strong",
            )}
          >
            In stock
          </button>
        </div>
      </div>

      {products.isError ? (
        <ErrorState error={products.error} onRetry={() => products.refetch()} />
      ) : products.isLoading ? (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {Array.from({ length: 8 }, (_, index) => (
            <ProductCardSkeleton key={index} />
          ))}
        </div>
      ) : total === 0 ? (
        <EmptyState
          icon={<PackageSearch aria-hidden className="size-5" />}
          title="Nothing matches that"
          description={
            search || categoryId || inStock
              ? "Try a different search, or clear the filters."
              : "The catalogue is empty. An administrator needs to add products."
          }
          action={
            (search || categoryId || inStock) && (
              <Button variant="secondary" onClick={() => setParams(new URLSearchParams())}>
                Clear filters
              </Button>
            )
          }
        />
      ) : (
        <>
          <div
            className={cn(
              "grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4",
              // Dim the grid while the next page loads, so it is visibly
              // busy without the layout collapsing.
              products.isFetching && "opacity-60 transition-opacity",
            )}
          >
            {products.data?.items.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>

          {pageCount > 1 && (
            <nav className="flex items-center justify-between border-t border-line pt-6" aria-label="Pagination">
              <Button
                variant="secondary"
                size="sm"
                disabled={page <= 1}
                onClick={() => setParams({ ...Object.fromEntries(params), page: String(page - 1) })}
              >
                Previous
              </Button>
              <p className="tabular text-sm text-muted">
                Page {page} of {pageCount}
              </p>
              <Button
                variant="secondary"
                size="sm"
                disabled={page >= pageCount}
                onClick={() => setParams({ ...Object.fromEntries(params), page: String(page + 1) })}
              >
                Next
              </Button>
            </nav>
          )}
        </>
      )}
    </div>
  );
}
