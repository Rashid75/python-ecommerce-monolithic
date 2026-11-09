import { NavLink, Link, Outlet, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { LogOut, Package, ShoppingBag, ShoppingCart, User2, MapPin } from "lucide-react";
import { request } from "@/lib/api";
import type { Cart } from "@/lib/types";
import { useAuth } from "@/hooks/authContext";
import { ThemeToggle } from "@/components/ThemeToggle";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/cn";

/** The cart count in the header, kept current by the same query the cart page uses. */
function CartIndicator() {
  const { user } = useAuth();
  const { data } = useQuery({
    queryKey: ["cart"],
    queryFn: () => request<Cart>("/cart"),
    enabled: Boolean(user),
  });
  const count = data?.total_items ?? 0;

  return (
    <NavLink
      to="/cart"
      className={({ isActive }) =>
        cn(
          "relative inline-flex size-9 items-center justify-center rounded-[--radius-control] transition-colors",
          isActive ? "bg-brand-50 text-brand-700 dark:bg-brand-700/20 dark:text-brand-300" : "text-muted hover:bg-ink-100 hover:text-heading dark:hover:bg-surface-raised",
        )
      }
      aria-label={count > 0 ? `Cart, ${count} items` : "Cart, empty"}
    >
      <ShoppingCart aria-hidden className="size-4" />
      {count > 0 && (
        <span className="tabular absolute -right-0.5 -top-0.5 flex min-w-4 items-center justify-center rounded-full bg-brand-600 px-1 text-[10px] font-semibold leading-4 text-white">
          {count > 99 ? "99+" : count}
        </span>
      )}
    </NavLink>
  );
}

const NAV = [
  { to: "/", label: "Shop", icon: ShoppingBag, end: true },
  { to: "/orders", label: "Orders", icon: Package, end: false },
  { to: "/addresses", label: "Addresses", icon: MapPin, end: false },
];

export function Layout() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="flex min-h-dvh flex-col">
      {/* Skip link: the first thing keyboard and screen-reader users reach,
          so they are not made to tab through the whole header on every
          page. Visible only when focused. */}
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-[--radius-control] focus:bg-brand-600 focus:px-4 focus:py-2 focus:text-sm focus:font-medium focus:text-white"
      >
        Skip to content
      </a>

      <header className="sticky top-0 z-40 border-b border-line bg-surface/85 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-6xl items-center gap-2 px-4 sm:px-6">
          <Link to="/" className="mr-2 flex items-center gap-2 font-semibold text-heading">
            <span className="flex size-8 items-center justify-center rounded-[--radius-control] bg-brand-600 text-white">
              <ShoppingBag aria-hidden className="size-4" />
            </span>
            <span className="hidden sm:inline">Northline</span>
          </Link>

          {user && (
            <nav className="flex items-center gap-1" aria-label="Main">
              {NAV.map(({ to, label, icon: Icon, end }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={end}
                  className={({ isActive }) =>
                    cn(
                      "inline-flex h-9 items-center gap-2 rounded-[--radius-control] px-3 text-sm font-medium transition-colors",
                      isActive
                        ? "bg-brand-50 text-brand-700 dark:bg-brand-700/20 dark:text-brand-300"
                        : "text-body hover:bg-ink-100 hover:text-heading dark:hover:bg-surface-raised",
                    )
                  }
                >
                  <Icon aria-hidden className="size-4" />
                  <span className="hidden sm:inline">{label}</span>
                </NavLink>
              ))}
            </nav>
          )}

          <div className="ml-auto flex items-center gap-1">
            <ThemeToggle />
            {user ? (
              <>
                <CartIndicator />
                <div className="ml-1 hidden items-center gap-2 border-l border-line pl-3 sm:flex">
                  <span className="flex size-7 items-center justify-center rounded-full bg-ink-100 text-xs font-semibold uppercase text-ink-600 dark:bg-surface-raised dark:text-ink-300">
                    {user.email.slice(0, 1)}
                  </span>
                  <span className="max-w-36 truncate text-sm text-body" title={user.email}>
                    {user.email}
                  </span>
                </div>
                <button
                  onClick={() => {
                    signOut();
                    navigate("/signin");
                  }}
                  aria-label="Sign out"
                  className="inline-flex size-9 items-center justify-center rounded-[--radius-control] text-muted transition-colors hover:bg-ink-100 hover:text-heading dark:hover:bg-surface-raised"
                >
                  <LogOut aria-hidden className="size-4" />
                </button>
              </>
            ) : (
              <Button size="sm" icon={<User2 aria-hidden className="size-4" />} onClick={() => navigate("/signin")}>
                Sign in
              </Button>
            )}
          </div>
        </div>
      </header>

      <main id="main" className="mx-auto w-full max-w-6xl flex-1 px-4 py-8 sm:px-6 sm:py-10">
        <Outlet />
      </main>

      <footer className="border-t border-line py-6">
        <div className="mx-auto max-w-6xl px-4 text-xs text-muted sm:px-6">
          Northline — a demonstration storefront for the Python Ecommerce API. No real payments are
          taken.
        </div>
      </footer>
    </div>
  );
}
