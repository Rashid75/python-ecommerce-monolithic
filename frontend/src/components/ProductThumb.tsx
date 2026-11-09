import { cn } from "@/lib/cn";
import type { Product } from "@/lib/types";

/**
 * A product tile standing in for a photograph the API does not store.
 *
 * Deterministic from the SKU, so a product keeps the same tile across
 * reloads and pages - one that changes colour when you navigate back looks
 * broken.
 *
 * The hue is pulled into a narrow band around the brand and the chroma
 * kept low. A full-spectrum random gradient per product is the obvious
 * implementation and it looks like a placeholder generator: saturated
 * magenta beside saturated orange reads as "no designer saw this". A tonal
 * family reads as a catalogue whose photography has not loaded yet, which
 * is the honest impression to give.
 */
export function ProductThumb({ product, large = false }: { product: Product; large?: boolean }) {
  const seed = [...product.sku].reduce((total, char) => total + char.charCodeAt(0), 0);
  // 255-315: indigo through violet, the brand's own neighbourhood.
  const hue = 255 + (seed % 61);
  const initials = product.name
    .replace(/[^a-zA-Z ]/g, "")
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0])
    .join("")
    .toUpperCase();

  return (
    <div
      aria-hidden
      className={cn(
        "relative flex aspect-4/3 items-center justify-center overflow-hidden",
        large && "rounded-[--radius-card]",
      )}
      style={{
        backgroundImage: `linear-gradient(145deg, oklch(0.95 0.025 ${hue}), oklch(0.88 0.045 ${hue + 18}))`,
      }}
    >
      {/* A faint grid, so the tile has some texture instead of reading as a
          flat swatch. */}
      <div
        className="absolute inset-0 opacity-[0.07]"
        style={{
          backgroundImage:
            "linear-gradient(to right, currentColor 1px, transparent 1px), linear-gradient(to bottom, currentColor 1px, transparent 1px)",
          backgroundSize: "14px 14px",
          color: `oklch(0.35 0.08 ${hue})`,
        }}
      />
      <span
        className={cn("relative font-semibold tracking-tight", large ? "text-5xl" : "text-2xl")}
        style={{ color: `oklch(0.46 0.1 ${hue})` }}
      >
        {initials}
      </span>
    </div>
  );
}
