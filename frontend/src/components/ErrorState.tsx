import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { ApiError } from "@/lib/api";

/**
 * What a page shows when a request failed.
 *
 * Deliberately shows the API's own message. The backend was built so that
 * every message is safe to display - internal exception text never leaves
 * it - which means repeating it here tells the customer something true
 * instead of a generic apology.
 */
export function ErrorState({ error, onRetry }: { error: unknown; onRetry?: () => void }) {
  const message =
    error instanceof ApiError ? error.message : "Something went wrong. Please try again.";

  return (
    <div className="flex flex-col items-center justify-center rounded-[--radius-card] border border-critical-500/25 bg-critical-50/60 px-6 py-14 text-center dark:bg-critical-700/10">
      <AlertTriangle aria-hidden className="mb-3 size-6 text-critical-600" />
      <h3 className="text-base font-semibold text-heading">That did not work</h3>
      <p className="mt-1 max-w-md text-sm text-body">{message}</p>
      {onRetry && (
        <Button variant="secondary" className="mt-6" onClick={onRetry}>
          Try again
        </Button>
      )}
    </div>
  );
}
