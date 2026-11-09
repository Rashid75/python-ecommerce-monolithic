import type { ReactNode } from "react";

/**
 * What a page shows when there is genuinely nothing to show.
 *
 * An empty list rendered as a blank area looks like a bug. This says what
 * is missing and gives the one action that fixes it.
 */
export function EmptyState({
  icon,
  title,
  description,
  action,
}: {
  icon: ReactNode;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-[--radius-card] border border-dashed border-line px-6 py-16 text-center">
      <div className="mb-4 flex size-12 items-center justify-center rounded-full bg-ink-100 text-muted dark:bg-surface-raised">
        {icon}
      </div>
      <h3 className="text-base font-semibold text-heading">{title}</h3>
      <p className="mt-1 max-w-sm text-sm text-muted">{description}</p>
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}
