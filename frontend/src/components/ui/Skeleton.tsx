import { cn } from "@/lib/cn";

/**
 * A placeholder shaped like the thing that is loading.
 *
 * Preferred over a spinner because it keeps the layout the same size
 * before and after the data lands, so the page does not jump as content
 * arrives - which is both unpleasant and a way to mis-click.
 */
export function Skeleton({ className }: { className?: string }) {
  return <div aria-hidden className={cn("skeleton rounded-md", className)} />;
}
