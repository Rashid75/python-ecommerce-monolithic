import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { ApiError } from "@/lib/api";
import { AuthProvider } from "@/hooks/useAuth";
import { useAuth } from "@/hooks/authContext";
import { ToastProvider } from "@/hooks/useToast";
import { Layout } from "@/components/Layout";
import { Products } from "@/pages/Products";
import { ProductDetail } from "@/pages/ProductDetail";
import { CartPage } from "@/pages/CartPage";
import { Checkout } from "@/pages/Checkout";
import { Orders } from "@/pages/Orders";
import { OrderDetail } from "@/pages/OrderDetail";
import { Addresses } from "@/pages/Addresses";
import { SignIn } from "@/pages/SignIn";
import { ButtonLink } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Data is considered fresh for half a minute. Without this, every
      // navigation refetches everything and the interface flickers through
      // loading states for data it already had.
      staleTime: 30_000,
      // Refetching on tab focus is right for prices and stock, which other
      // people change.
      refetchOnWindowFocus: true,
      retry: (failureCount, error) => {
        // Never retry something the server refused on purpose. A 401, a
        // 404 or a 409 will say exactly the same thing the second time,
        // and retrying a 409 from checkout would hammer a path that holds
        // database locks.
        if (error instanceof ApiError && error.status >= 400 && error.status < 500) return false;
        return failureCount < 2;
      },
    },
    mutations: {
      // Mutations are never retried automatically. Checkout and payment
      // are not safe to repeat without the idempotency key the component
      // supplies deliberately.
      retry: false,
    },
  },
});

/** A route only a signed-in customer may see. */
function RequireAuth({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  // Until the stored token has been checked, neither state is known. Showing
  // the sign-in page here would bounce a signed-in customer out of their own
  // session on every hard refresh.
  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64" />
      </div>
    );
  }

  if (!user) {
    // Remembers where they were going, so signing in returns them there.
    return <Navigate to="/signin" replace state={{ from: location.pathname }} />;
  }

  return <>{children}</>;
}

function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <p className="tabular text-5xl font-semibold tracking-tight text-heading">404</p>
      <h1 className="mt-3 text-lg font-semibold">That page does not exist</h1>
      <p className="mt-1 text-sm text-muted">The link may be old, or the address mistyped.</p>
      <ButtonLink to="/" className="mt-6">
        Back to the shop
      </ButtonLink>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <ToastProvider>
            <Routes>
              <Route element={<Layout />}>
                {/* Public: browsing the catalogue needs no account, which
                    matches the API - product reads are unauthenticated. */}
                <Route index element={<Products />} />
                <Route path="products/:id" element={<ProductDetail />} />
                <Route path="signin" element={<SignIn mode="signin" />} />
                <Route path="register" element={<SignIn mode="register" />} />

                <Route
                  path="cart"
                  element={
                    <RequireAuth>
                      <CartPage />
                    </RequireAuth>
                  }
                />
                <Route
                  path="checkout"
                  element={
                    <RequireAuth>
                      <Checkout />
                    </RequireAuth>
                  }
                />
                <Route
                  path="orders"
                  element={
                    <RequireAuth>
                      <Orders />
                    </RequireAuth>
                  }
                />
                <Route
                  path="orders/:id"
                  element={
                    <RequireAuth>
                      <OrderDetail />
                    </RequireAuth>
                  }
                />
                <Route
                  path="addresses"
                  element={
                    <RequireAuth>
                      <Addresses />
                    </RequireAuth>
                  }
                />

                <Route path="*" element={<NotFound />} />
              </Route>
            </Routes>
          </ToastProvider>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
