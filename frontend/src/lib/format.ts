/** Display formatting. Nothing here changes a value, only how it reads. */

/**
 * Format a decimal string as money.
 *
 * Takes the string the API sent and never converts it to a number for
 * arithmetic - Intl is given the string parsed only for grouping and
 * symbol placement, and the backend has already decided the amount.
 */
export function money(amount: string, currency = "BHD"): string {
  const parsed = Number(amount);
  if (Number.isNaN(parsed)) return amount;
  return new Intl.NumberFormat("en-BH", {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
  }).format(parsed);
}

export function dateTime(iso: string): string {
  return new Intl.DateTimeFormat("en-GB", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(iso));
}

export function date(iso: string): string {
  return new Intl.DateTimeFormat("en-GB", { dateStyle: "medium" }).format(new Date(iso));
}
