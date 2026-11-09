import { useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { ShoppingBag } from "lucide-react";
import { ApiError } from "@/lib/api";
import { useAuth } from "@/hooks/authContext";
import { Button } from "@/components/ui/Button";
import { Field } from "@/components/ui/Field";
import { Card } from "@/components/ui/Card";

type Mode = "signin" | "register";

export function SignIn({ mode }: { mode: Mode }) {
  const { signIn, register } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<ApiError | null>(null);
  const [busy, setBusy] = useState(false);

  // Where the customer was trying to go before being sent here. Sending
  // them back afterwards is the difference between signing in and losing
  // your place.
  const from = (location.state as { from?: string } | null)?.from ?? "/";

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setBusy(true);
    try {
      if (mode === "signin") await signIn(email, password);
      else await register(email, password);
      navigate(from, { replace: true });
    } catch (caught) {
      setError(caught instanceof ApiError ? caught : new ApiError(0, "error", "Something went wrong."));
    } finally {
      setBusy(false);
    }
  }

  const registering = mode === "register";

  return (
    <div className="mx-auto flex max-w-md flex-col justify-center py-8">
      <div className="mb-8 text-center">
        <span className="mx-auto mb-4 flex size-11 items-center justify-center rounded-[--radius-card] bg-brand-600 text-white">
          <ShoppingBag aria-hidden className="size-5" />
        </span>
        <h1 className="text-2xl font-semibold tracking-tight">
          {registering ? "Create an account" : "Welcome back"}
        </h1>
        <p className="mt-1 text-sm text-muted">
          {registering ? "It takes an email and a password." : "Sign in to shop and see your orders."}
        </p>
      </div>

      <Card className="p-6">
        <form onSubmit={submit} className="space-y-4" noValidate>
          <Field
            label="Email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            error={error?.fieldErrors.email}
          />
          <Field
            label="Password"
            type="password"
            // Tells a password manager whether to offer a saved password or
            // generate a new one. Wrong value here is why autofill so
            // often does the unhelpful thing.
            autoComplete={registering ? "new-password" : "current-password"}
            required
            minLength={registering ? 8 : undefined}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            error={error?.fieldErrors.password}
            hint={registering ? "At least 8 characters." : undefined}
          />

          {/* The API answers every sign-in failure identically on purpose,
              so that the response cannot be used to discover who has an
              account. Showing its message verbatim keeps that property. */}
          {error && Object.keys(error.fieldErrors).length === 0 && (
            <p role="alert" className="rounded-[--radius-control] bg-critical-50 px-3 py-2 text-sm font-medium text-critical-700 dark:bg-critical-700/15 dark:text-critical-500">
              {error.message}
            </p>
          )}

          <Button type="submit" fullWidth size="lg" loading={busy}>
            {registering ? "Create account" : "Sign in"}
          </Button>
        </form>
      </Card>

      <p className="mt-6 text-center text-sm text-muted">
        {registering ? "Already have an account? " : "No account yet? "}
        <Link
          to={registering ? "/signin" : "/register"}
          state={{ from }}
          className="font-medium text-brand-600 hover:underline"
        >
          {registering ? "Sign in" : "Create one"}
        </Link>
      </p>
    </div>
  );
}
