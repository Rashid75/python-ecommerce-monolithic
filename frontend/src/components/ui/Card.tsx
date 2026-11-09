import type { ReactNode } from "react";
import { cn } from "@/lib/cn";

export function Card({ className, children }: { className?: string; children: ReactNode }) {
  return (
    <div
      className={cn(
        "rounded-[--radius-card] border border-line bg-surface shadow-subtle",
        className,
      )}
    >
      {children}
    </div>
  );
}
