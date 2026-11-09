import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Join class names, with later Tailwind classes winning over earlier ones.
 *
 * Without twMerge, `cn("px-4", "px-6")` produces both and the result
 * depends on stylesheet order - which is how a component's `className`
 * prop silently stops overriding anything.
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
