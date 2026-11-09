import { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";

const KEY = "ecommerce.theme";

/**
 * Light and dark, remembered.
 *
 * Defaults to the operating system's preference rather than to light, and
 * only overrides it once someone chooses. Reading the stored value before
 * first paint happens in index.html, so the page never flashes white
 * before turning dark.
 */
export function ThemeToggle() {
  const [dark, setDark] = useState(() => document.documentElement.classList.contains("dark"));

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    try {
      localStorage.setItem(KEY, dark ? "dark" : "light");
    } catch {
      /* blocked site data: the choice simply does not persist */
    }
  }, [dark]);

  return (
    <button
      onClick={() => setDark((value) => !value)}
      aria-label={dark ? "Switch to light theme" : "Switch to dark theme"}
      className="inline-flex size-9 items-center justify-center rounded-[--radius-control] text-muted transition-colors hover:bg-ink-100 hover:text-heading dark:hover:bg-surface-raised"
    >
      {dark ? <Moon aria-hidden className="size-4" /> : <Sun aria-hidden className="size-4" />}
    </button>
  );
}
